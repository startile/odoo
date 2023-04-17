# -*- coding: utf-8 -*-
{
    'name': 'Startile Customization',
    'summary': 'Startile Customization',
    'description': "",
    'author': 'Keypress IT Services',
    'version': '16.0.1.0.0',
    'sequence' : 1,
    'website' : 'https://www.keypress.co.in',
    'depends':['purchase'],
    'data': [
        'views/res_config_settings_view.xml',
        'templates/purchase_mail_template.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
