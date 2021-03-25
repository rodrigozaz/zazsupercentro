# -- coding: utf-8 --
{
    'name': 'Materiales product report for all warehouse',

    'summary': 'Materiales product report for all warehouse',

    'description': """
    task id: 2439508

     Materiales Castelar :  Stock report per product for all warehouse
    
    """,
    'author': 'Odoo',
    'website': 'https://www.odoo.com/',

    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OEEL-1',

    # any module necessary for this one to work correctly
    'depends': ['product','sale'],

    # always loaded
    'data': [
        "views/product_warehouse_template.xml",
        "views/product_warehouse_report.xml",
        "views/product_warehouse_form.xml",
    ],
    # only loaded in demonstration mode
    'demo': [],
    'application': False,
}
