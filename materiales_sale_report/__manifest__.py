# -- coding: utf-8 --
{
    'name': 'Materiales Sales Report',

    'summary': 'Materiales Daily Closing Sales Report',

    'description': """
    task id: 2315386

     Materiales Castelar : Daily Closing Sales Report 
     a pdf that can be generated from the accounting app
    
    """,
    'author': 'Odoo',
    'website': 'https://www.odoo.com/',

    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OEEL-1',

    # any module necessary for this one to work correctly
    'depends': ['account','web','sale'],

    # always loaded
    'data': [
        "security/ir.model.access.csv",
        'views/payment_inherit_form.xml',
        "views/sales_report_template.xml",
        "views/sales_report.xml",
        "views/sales_report_materiales.xml",
    ],
    # only loaded in demonstration mode
    'demo': [],
    'application': False,
}
