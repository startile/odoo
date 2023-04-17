from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self,vals):
        res = super(PurchaseOrder,self).create(vals)
        mail_template = self.env.ref('kits_startile_customization.purchase_email_template_notity_users')
        notify_users = self.env['ir.config_parameter'].sudo().get_param('purchase_notify_users')
        if notify_users:
            notify_partners = self.sudo().env['res.users'].search([('id','in',eval(notify_users) or [])]).mapped('partner_id')
            for partner in notify_partners:
                mail_template.with_context(notify_partner_id=partner).send_mail(res.id,email_values={'email_to': partner.email},force_send=True)
        return res
