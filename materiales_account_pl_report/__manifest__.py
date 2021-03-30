# -*- coding: utf-8 -*-
{
    'name': "Materiales Castelar : Accounting report customization",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Task ID: 2450247
        In Accounting, the report Profit and Loss, when seeing all the stores (consolidated), looks fine for Materiales Castelar.
        If they select 1 store/branch, also the report is ok.
        When selecting more than 1 store/branch, Odoo adds the amounts and shows 1 single column with the results:
        This is expected behavior and Materiales Castelar wants a modification to the report, showing every selected store as a column so they can see all of them side by side and in the last column, the total for all of them. 
        The report should allow displaying the 11 stores/branches on the same screen, each of them with their own amounts and at the end, the total as it's displayed by Odoo. This report will be exported to excel, the same way that it works right now.

    """,

    'author': "Odoo Inc",
    'website': "http://www.odoo.com",
    'category': 'Custom Development',
    'license': 'OEEL-1',
    'version': '0.1',
    'depends': ['base', 'account_accountant'],
    'data': []
}
