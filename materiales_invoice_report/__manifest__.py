# -*- coding: utf-8 -*-
{
    'name': "Materiales Castelar: New Report - Margins per customer per invoice",
    'summary': 'Report for margins of customer based on invoice',
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com',
    'version': '1.1',
    'author': 'Odoo Inc',
    'description': """
        Task ID: 2451466
        - Generate Custom report based on the customer and invoice
    """,
    'category': 'Custom Development',

    # any module necessary for this one to work correctly
    'depends': ['account_accountant'],

    # always loaded
    'data': [
        "views/account_journal_views.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}