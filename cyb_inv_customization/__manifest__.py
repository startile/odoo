# -*- coding: utf-8 -*-
{
    'name': "cyb_inv_customization",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/invoice_report_inherit.xml',
        'views/account_move_form_inherit.xml',
    ],
    'application': True,
    'installable': True,
}
