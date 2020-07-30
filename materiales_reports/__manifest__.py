# -- coding: utf-8 --
{
    'name': '',
    'summary': '',
    'description': 
    """""",
    'author': 'Odoo',
    'website': 'https://www.odoo.com/',

    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OEEL-1',

    # any module necessary for this one to work correctly
    'depends': ['purchase','account','sale',],

    # always loaded
    'data': [
        'views/purchase_report.xml',
        'views/sale_report.xml',
        'views/account_report.xml',
        'views/payment_receipt.xml'
    ],
    # only loaded in demonstration mode
    'application': False,
}
