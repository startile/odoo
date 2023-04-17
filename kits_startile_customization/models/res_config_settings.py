from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    notify_user_ids = fields.Many2many('res.users', 'rel_purchase_setting_users', 'purchase_id', 'user_id', string="Notify Users")

    def get_values(self):
        config_obj = self.env['ir.config_parameter'].sudo()
        res = super(ResConfigSettings, self).get_values()
        res['notify_user_ids'] = eval(
            config_obj.get_param('purchase_notify_users', '[]'))
        return res

    def set_values(self):
        config_obj = self.env['ir.config_parameter'].sudo()
        config_obj.set_param(
            'purchase_notify_users',
            self.notify_user_ids.ids
        )
        return super(ResConfigSettings, self).set_values()