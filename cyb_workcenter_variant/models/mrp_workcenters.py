# -*- coding: utf-8 -*-

from odoo import models, fields, _


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    def action_check_variants_in_product_template(self):
        ctx = {
            'default_capacity_ids': self.capacity_ids,
            'default_active_id': self.id,
        }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Select Products to fetch difference'),
            'view_mode': 'form',
            'res_model': 'workcenter.variant.check.wizard',
            'target': 'new',
            'context': ctx,
        }

    missing_variant_ids = fields.One2many('workcenter.missing.variant', 'workcenter_id',
                                          string="Missing Product Variants")

    def action_add_variants_to_capacities(self):
        for rec in self:
            new_capacity_ids = []
            if rec.missing_variant_ids:
                for variant in rec.missing_variant_ids:
                    new_capacity_ids.append((0, 0, {
                        'product_id': variant.product_id.id,
                        'capacity': 200,
                    }))
            if new_capacity_ids:
                rec.write({
                    'capacity_ids': new_capacity_ids,
                })
            rec.missing_variant_ids.unlink()


class WorkcenterMissingVariant(models.Model):
    _name = "workcenter.missing.variant"
    _description = "Missing Product Variant in Workcenter"

    workcenter_id = fields.Many2one('mrp.workcenter', required=True)
    product_id = fields.Many2one('product.product', string="Product Variant", required=True)
