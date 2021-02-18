# -- coding: utf-8 --
{
    'name': 'Materiales Product Report',

    'summary': 'Materiales Product report',
    'author': 'Odoo',
    'website': 'https://www.odoo.com/',

    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OEEL-1',

    # any module necessary for this one to work correctly
    'depends': ['stock','product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/product_report_form.xml',
        'views/product_report_pdf.xml',
        'views/product_report_template.xml'
    ],

    'application': False,
}
