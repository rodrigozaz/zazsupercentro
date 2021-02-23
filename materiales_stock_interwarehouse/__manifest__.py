# -*- coding: utf-8 -*-
{
    'name': "Materiales Castelar : Restrictions for transfer inter-warehouse (stores)",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Task ID: 2440159
        1. Destination warehouse, who needs product, creates a transfer in the Inventory app, selecting the origin warehouse (user should be able to see 
           all the warehouses in the origin location field) and in the destination location field, by default, it should show the location(s) in the 
           warehouse(s) that the user has assigned. Most of the users have only 1 warehouse assigned and it should show only that one as destination location. 
           Then, he will add the product(s) that he is requesting from the other warehouse.
        2. Once the transfer is created and saved, he should see a button that says "Request transfer". He shouldn't be able to see the button "Validate"
        3. When clicking the button "Request transfer", the user in the origin location should receive an email telling him about the pending transfer 
           and the transfer should change status to "Pending approval". It is important that the user should see only transfers that belong to the warehouse 
           he is assigned to. 
        4. The user from the origin location will enter to odoo and approve/validate the transfer. In the moment that the user approves the transfer, the 
           product movement should happen, sending the product from the origin location to the destination location. 
        5. Only users in the Inventory Administrator group should receive the notification email about the pending transfer in their origin warehouse.
    """,

    'author': "Odoo Inc",
    'website': "http://www.odoo.com",
    'category': 'Custom Development',
    'license': 'OEEL-1',
    'version': '0.1',
    'depends': ['stock', 'sale_store'],
    'data': [
        'views/email_template.xml',
        'views/stock_picking_views.xml',
    ],
}