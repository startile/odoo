# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkcenterVariantCheckWizard(models.TransientModel):
    _name = 'workcenter.variant.check.wizard'
    _description = 'Workcenter Variant Check Wizard'

    product_template_ids = fields.Many2many('product.template', string="Product Templates")

    def action_submit_variant_check(self):
        workcenter = self.env['mrp.workcenter'].browse(self.env.context.get('active_id'))

        existing_variants = workcenter.capacity_ids.mapped('product_id.id')
        selected_templates = self.product_template_ids

        new_variants = selected_templates.mapped('product_variant_ids').filtered(
            lambda v: v.id not in existing_variants
        )

        workcenter.missing_variant_ids.unlink()
        for variant in new_variants:
            self.env['workcenter.missing.variant'].create({
                'workcenter_id': workcenter.id,
                'product_id': variant.id
            })
