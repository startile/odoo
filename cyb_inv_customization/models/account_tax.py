# -*- coding: utf-8 -*-

from odoo import models, api


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def _prepare_tax_totals(self, base_lines, currency, tax_lines=None):
        res = super(AccountTax, self)._prepare_tax_totals(base_lines=base_lines, currency=currency, tax_lines=tax_lines)
        amount_total_without_symbol = res['formatted_amount_total'].lstrip(currency.symbol)
        amount_untaxed_without_symbol = res['formatted_amount_untaxed'].lstrip(currency.symbol)
        res['formatted_amount_total'] = amount_total_without_symbol
        res['formatted_amount_untaxed'] = amount_untaxed_without_symbol
        return res
