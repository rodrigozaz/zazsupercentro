# -*- coding: utf-8 -*-
{
    'name': 'Materiales Castelar',
    'summary': 'Materiales Castelar',
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com',
    'version': '1.1',
    'author': 'Odoo Inc',
    'description': """
    - Raise a validation error if the done quantity is greater than demand
    """,
    'category': 'Custom Development',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}