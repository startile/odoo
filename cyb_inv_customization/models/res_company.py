# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    startile_installation_instruction = fields.Html(string='Star-Tile Installation Instruction')
    t_and_c_upon_delivery = fields.Html(string='Star-Tile Terms')
