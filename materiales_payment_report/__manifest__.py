# -*- coding: utf-8 -*-
{
    'name': "Materiales: Vendor payment report",

    'summary': """
       Materiales: Vendor payment report
    """,

    'description': """
        Task ID: 2451481

        Odoo will generate a report (pdf) with the following information:

            1. In the header:

            1.1 Vendor name

            1.2 Payment date

            2. In the body, a table with the following information:

            2.1 Payment Number

            2.2 Journal

            2.3 Total paid

            2.4 Invoices related to that payment
        
     """,

    'author': "Odoo PS-US",
    'website': "http://www.odoo.com",
    'license': 'OEEL-1',

    'category': 'Custom Development',
    'version': '0.1',

    'depends': ['account'],

    'data': [
        'views/vendor_payment_form.xml',
        'views/vendor_payment_report.xml',
        'views/vendor_payment_template.xml'
    ],
}