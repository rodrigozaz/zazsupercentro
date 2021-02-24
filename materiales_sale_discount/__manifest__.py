# -*- coding: utf-8 -*-
{
    'name': "Materiales Castelar : Sales discount control per user",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Task ID: 2450255
        1. When a user gets access rights for the Sales app, a new field should appear to set the discount limit that the user will have and a "Responsible" to authorize higher discounts (this should be an existing user from the database).
        1.1 The limit will be set as a percentage.
        2. in the sales app, when the user is creating a sales order, in the sales line, the discount field should only allow him to enter a number equal or lesser than the limit set in his user information.
        3. If the user tries to enter a higher discount than the limit set in his user information, he will get a warning saying that the discount is higher than their allowed discount and the user should be able to save the quotation but not confirm it.  Here, there are 2 options for the user:
        3.1 The user will be able to confirm the order if changes the discount to a number that is within his limit.
        3.2 We will need a new button on the screen to "Request Authorization". When they click this button, the responsible set in settings should receive an email saying that he has a quotation pending authorization due to the discount set in the order. 
        4. The responsible will go to the quotation and:
        4.1 If they authorize the discount, the salesperson will receive an email/notification saying that the quotation is ready to confirm.
        4.2 If they reject the discount, the salesperson will receive an email and could cancel the order or modify the discount.
    """,

    'author': "Odoo Inc",
    'website': "http://www.odoo.com",
    'category': 'Custom Development',
    'license': 'OEEL-1',
    'version': '0.1',
    'depends': ['base', 'sale'],
    'data': [
        'views/email_template.xml',
        'views/sale_views.xml',
        'views/res_users_views.xml',
    ],
}