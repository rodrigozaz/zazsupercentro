# -*- coding: utf-8 -*-
{
    'name': 'Materiales Materiales Castelar : Specific vendor pricelists for agreements',

    'summary': 'Specific vendor pricelists for agreements',

    'description': """
    1. Create agreements in the new model.
    2. Create new records in vendor pricelists using the agreements.
    3. Create RFQs selecting the vendor/agreement and adding products.
    4. Verify that the prices and discounts match with the prices added
       in the vendor pricelist
    """,

    'author': 'Odoo',
    'website': 'https://www.odoo.com/',

    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OEEL-1',

    # any module necessary for this one to work correctly
    'depends': ['sale','purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/pricelist_agreement_views.xml',
        'views/product_pricelist_views.xml',
        'views/product_supplierinfo_views.xml',
        'views/purchase_order_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
    ],
    # only loaded in demonstration mode
    'application': False,
}
