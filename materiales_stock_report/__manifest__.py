# -- coding: utf-8 --
{
    'name': 'Materiales Stock Report',

    'summary': 'Materiales Detailed stock report',

    'description': """
    task id: 2325441

    New Report - Detailed Inventory Report by Warehouse
    """,

    'author': 'Odoo',
    'website': 'https://www.odoo.com/',

    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OEEL-1',

    # any module necessary for this one to work correctly
    'depends': ['web','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/action_detailed_stock.xml',
        'views/detailed_report_form.xml',
        'views/detailed_report_template.xml'

    ],
    # only loaded in demonstration mode
    'application': False,
}
