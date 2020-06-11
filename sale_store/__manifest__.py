# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Sales by Stores",
    'version': '1.0',
    'depends': ['sale_management', 'sale_stock', 'purchase_stock'],
    'author': 'Odoo Inc',
    'license': 'OEEL-1',
    'maintainer': 'Odoo Inc',
    'category': 'Sales',
    'description': """
Sales By Stores(Warehouse):
==========================
- Feature 1:
    Functionality to assign warehouse(s) to a user and on sales order warehouse should be changed based on
     the salesperson.
- Feature 2:
    Functionality to restrict user from accessing other warehouse documents then the warehouses assigend to them.
    Documents such as sale orders, delivery orders, invoices
- Feature 3:
    Functionality to show the users quantity available on any warehouse via inventory rreport. 
    So that they mey know product available at which store(warehouse).
- Feature 4:
    Functionality to restrict all inventory documents based on the warehouses assigend to them and the locations
    of those warehouses.
- [ADD] Additional Requirement:
    Added a warehouse field on purchase order.
    Added a sequence field on warehouse configuration.
    On PO creation if the po has picking type associated the sequence for the pos is based on the sequence on
    the warehouse associated with the picking type
    """,
    # data files always loaded at installation
    'data': [
        'security/sale_store_security.xml',
        'views/res_users_views.xml',
        'views/stock_views.xml',
        'views/purchase_views.xml',
    ],
}