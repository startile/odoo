# -*- coding: utf-8 -*-

import io
from base64 import b64encode

import xlsxwriter
from odoo import models, fields, api, _
from odoo.tools import get_lang


class InvoiceReferenceImages(models.Model):
    _name = 'invoice.reference.images'

    move_id = fields.Many2one('account.move')
    image = fields.Image(string='Image', required=1)
    image_name = fields.Char()
    ir_attachment_id = fields.Many2one('ir.attachment')

    def _create_or_update_attachment(self):
        for rec in self:
            if rec.ir_attachment_id:
                rec.ir_attachment_id.write({
                    'datas': rec.image,
                })
            else:
                ir_attachment_id = self.env['ir.attachment'].create({
                    'name': f"Reference_Image_{rec.id}.png",
                    'type': 'binary',
                    'datas': rec.image,
                    'res_model': 'account.move',
                    'res_id': rec.move_id.id,
                    'mimetype': 'image/png',
                })
                rec.ir_attachment_id = ir_attachment_id.id

    @api.model
    def create(self, vals):
        record = super(InvoiceReferenceImages, self).create(vals)
        record._create_or_update_attachment()
        return record

    def write(self, vals):
        res = super(InvoiceReferenceImages, self).write(vals)
        self._create_or_update_attachment()
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'

    references_images_ids = fields.One2many('invoice.reference.images', 'move_id')

    def generate_xlsx_report(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Packing List")

        bold_center = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        bold_left = workbook.add_format({'bold': True, 'align': 'left', 'valign': 'vcenter'})
        normal_left = workbook.add_format({'align': 'left', 'valign': 'vcenter'})
        border_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
        title_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter'})

        sheet.set_column('A:A', 40)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 20)

        company = self.company_id
        company_name = company.name or ''
        company_address = f"{company.street or ''} | {company.street2 or ''} | {company.city or ''} | {company.zip or ''} | {company.country_id.name or ''}"

        sheet.merge_range('A1:C1', company_name, title_format)
        sheet.merge_range('A2:C2', company_address, normal_left)
        sheet.merge_range('C3:C3', company.phone or '', normal_left)
        partner = self.partner_id
        recipient_address = f"""
        {partner.name or ''}
        {partner.street or ''}
        {partner.street2 or ''}
        {partner.city or ''} {self.partner_id.zip or ''}
        {partner.country_id.name or ''}
        """
        sheet.merge_range('C4:C8', recipient_address, normal_left)

        sheet.merge_range('A9:C9', "Packing List", title_format)
        sheet.merge_range('A10:C10', f"Invoice {self.name}", bold_left)
        sheet.merge_range('A11:C11', f"Order Date: {self.invoice_date or ''}", normal_left)

        sheet.write('A13', "Description", bold_center)
        sheet.write('B13', "Quantity", bold_center)
        sheet.write('C13', "Unit Price", bold_center)

        row = 13
        for line in self.invoice_line_ids:
            row += 1
            sheet.write(row, 0, line.product_id.name or _('Undefined'), border_format)
            sheet.write(row, 1, f"{line.quantity} Units", border_format)
            sheet.write(row, 2, f"{line.price_unit:.2f}", border_format)

        workbook.close()
        output.seek(0)
        return output.getvalue()

    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref(self._get_mail_template(), raise_if_not_found=False)
        lang = False
        if template:
            lang = template._render_lang(self.ids)[self.id]
        if not lang:
            lang = get_lang(self.env).code
        compose_form = self.env.ref('account.account_invoice_send_wizard_form', raise_if_not_found=False)

        attachments = []
        if self._context.get('image_mode'):
            attachments += self.references_images_ids.mapped('ir_attachment_id').ids
            xlsx_data = self.generate_xlsx_report()
            xlsx_attachment = self.env['ir.attachment'].create({
                'name': f"Invoice_{self.name}.xlsx",
                'type': 'binary',
                'datas': b64encode(xlsx_data),
                'res_model': 'account.move',
                'res_id': self.id,
                'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            })
            attachments.append(xlsx_attachment.id)
            template.attachment_ids = [(6, 0, attachments)]
        else:
            template.attachment_ids = [(5, 0, 0)]
        ctx = dict(
            default_model='account.move',
            default_res_id=self.id,
            # For the sake of consistency we need a default_res_model if
            # default_res_id is set. Not renaming default_model as it can
            # create many side-effects.
            default_res_model='account.move',
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            default_email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature",
            model_description=self.with_context(lang=lang).type_name,
            force_email=True,
            active_ids=self.ids,
        )

        report_action = {
            'name': _('Send Invoice'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

        if self.env.is_admin() and not self.env.company.external_report_layout_id and not self.env.context.get(
                'discard_logo_check'):
            return self.env['ir.actions.report']._action_configure_external_report_layout(report_action)

        return report_action


class AccountInvoiceSend(models.TransientModel):
    _inherit = 'account.invoice.send'
