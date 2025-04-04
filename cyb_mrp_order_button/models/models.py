# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    mrp_production_id = fields.Many2one('mrp.production', string="Manufacturing Order",
                                        compute='_compute_mrp_production')

    @api.depends('name')
    def _compute_mrp_production(self):
        for order in self:
            # Look for an MRP with the SO name in the origin field
            mo = self.env['mrp.production'].search([
                ('origin', 'like', order.name),
                ('state', '!=', 'cancel')
            ], limit=1)
            order.mrp_production_id = mo

    def action_open_mrp_production(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Manufacturing Order',
            'view_mode': 'form',
            'res_model': 'mrp.production',
            'res_id': self.mrp_production_id.id,
            'target': 'current',
        }
