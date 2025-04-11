# -*- coding: utf-8 -*-
{
    'name': "cyb_workcenter_variant",
    'summary': "Short (1 phrase/line) summary of the module's purpose",
    'description': """Long description of module's purpose""",
    'author': "Zartash",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_workcenters.xml',
        'wizard/workcenter_variant_check_wizard.xml',
    ],
}

