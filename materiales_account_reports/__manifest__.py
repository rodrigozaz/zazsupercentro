# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
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

    'depends': [
        'account_accountant',
        'sale_margin',
        'sale_stock',
        'materiales_stock_orders',
    ],
    'data': [
        'views/account_move_report_view.xml',
    ],
    'auto_install': True,
    'installable': True,
}
