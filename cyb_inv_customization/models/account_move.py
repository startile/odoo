# -*- coding: utf-8 -*-
import base64
import imghdr
import io
from base64 import b64encode

import xlsxwriter
from odoo import models, fields, api, _
from odoo.tools import get_lang


class InvoiceReferenceAttachment(models.Model):
    _name = 'invoice.reference.attachment'

    move_id = fields.Many2one('account.move')
    attachment = fields.Binary(string='Attachments', required=1)
    attachment_name = fields.Char()
    ir_attachment_id = fields.Many2one('ir.attachment')

    def _create_or_update_attachment(self):
        for rec in self:
            if rec.ir_attachment_id:
                rec.ir_attachment_id.write({
                    'datas': rec.attachment,
                })
            else:
                ir_attachment_id = self.env['ir.attachment'].create({
                    'name': f"Reference_attachment_{rec.id}",
                    'type': 'binary',
                    'datas': rec.attachment,
                    'res_model': 'account.move',
                    'res_id': rec.move_id.id,
                    'mimetype': 'image/png',
                })
                rec.ir_attachment_id = ir_attachment_id.id

    @api.model
    def create(self, vals):
        record = super(InvoiceReferenceAttachment, self).create(vals)
        record._create_or_update_attachment()
        return record

    def write(self, vals):
        res = super(InvoiceReferenceAttachment, self).write(vals)
        self._create_or_update_attachment()
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'

    references_attachment_ids = fields.One2many('invoice.reference.attachment', 'move_id')

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
        {partner.city or ''} {partner.zip or ''}
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
        for line in self.invoice_line_ids.filtered(lambda x:x.display_type=='product'):
            row += 1
            sheet.write(row, 0, line.product_id.name or _('Undefined'), border_format)
            sheet.write(row, 1, f"{line.quantity} {line.product_uom_id.name}", border_format)
            sheet.write(row, 2, f"{line.price_unit:.2f}", border_format)

        workbook.close()
        output.seek(0)
        return output.getvalue()

    # def get_image_from_attachments(self):
    #     image_attachments = []
    #     for ref_attachment in self.references_attachment_ids:
    #         if ref_attachment.attachment:
    #             try:
    #                 decoded_image = base64.b64decode(ref_attachment.attachment, validate=True)
    #                 image_type = imghdr.what(None, decoded_image)
    #                 if image_type:
    #                     image_attachments.append(ref_attachment)
    #             except Exception:
    #                 pass
    #     return image_attachments

    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        if self._context.get('attachment_mode'):
            template = self.env.ref('cyb_inv_customization.email_template_sample_order_invoice',
                                    raise_if_not_found=False)
        else:
            template = self.env.ref(self._get_mail_template(), raise_if_not_found=False)
        lang = False
        if template:
            lang = template._render_lang(self.ids)[self.id]
        if not lang:
            lang = get_lang(self.env).code
        compose_form = self.env.ref('account.account_invoice_send_wizard_form', raise_if_not_found=False)

        attachments = []
        if self._context.get('attachment_mode'):
            # attachments += [attachment.id for attachment in self.get_image_from_attachments()]
            attachments += self.references_attachment_ids.mapped('ir_attachment_id').ids
            xlsx_data = self.generate_xlsx_report()
            xlsx_attachment = self.env['ir.attachment'].create({
                'name': f"Packing List {self.name}.xlsx",
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
