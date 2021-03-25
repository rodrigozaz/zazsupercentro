# -- coding: utf-8 --
{
    'name': 'Materiales Stock Orders Report',

    'summary': 'Materiales Stock Orders Report',

    'description': """
    task id: 2450260

     Materiales Castelar : 
    
    """,
    'author': 'Odoo',
    'website': 'https://www.odoo.com/',

    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OEEL-1',

    # any module necessary for this one to work correctly
    'depends': ['account','material_castler_pricelist'],

    # always loaded
    'data': [
        'views/account_move_inherit.xml',
        'views/res_partner_inherit.xml',
        'wizards/invoice_stock_action.xml',
        'wizards/invoice_stock_form.xml',
        'wizards/invoice_stock_template.xml'
        
    ],
    # only loaded in demonstration mode
    'demo': [],
    'application': False,
}