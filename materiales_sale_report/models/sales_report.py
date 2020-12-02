# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime

class WarehouseSales(models.Model):
    _name = 'warehouse.sales'
    _description = 'Daily sales by warehouse'

    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    warehouse_ids = fields.Many2many('stock.warehouse', compute="_compute_warehouses")
    warehouse_id = fields.Many2one('stock.warehouse', string= 'Sucursal',required=True,)    
    report_date = fields.Date(string= 'Fecha de Reporte',required=True)

    @api.depends('user_id')
    def _compute_warehouses(self):
        for rec in self:
            rec.warehouse_ids = rec.user_id.warehouse_ids

    def print_pdf_warehouse_sales(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'warehouse': self.warehouse_id.id,
                'date': self.report_date,
            },
        }
        return self.env.ref('materiales_sale_report.action_daily_sale_warehouse').report_action(self, data=data)

class ReportAttendanceRecap(models.AbstractModel):

    _name = 'report.materiales_sale_report.daily_sale_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        location_id = data['form']['warehouse']
        report_date = data['form']['date']

        location_info = self.env['stock.warehouse'].search_read([('id','=', location_id)])[0]
        location = {
            'name':location_info['name'],
            'id':location_info['id']
        }

        
        invoices = self.env['account.move'].search_read([('invoice_date','=',report_date),('warehouse_id','=',location['id']),('type','=','out_invoice')])

        invoices.sort(key=lambda i: int(i['name'].split('/')[-1]))
        last_invoice = 0
        if len(invoices) >= 1:
            last_invoice = int(invoices[0]['name'].split('/')[-1]) - 1

        old_payments = self.env['account.payment'].search([('payment_date','=',report_date),('state','not in',['draft','cancelled']), ('partner_type', '=', 'customer')])
        old_inv_ids = []
        for payments in old_payments:
            
            for inv in payments.invoice_ids:
                if inv.warehouse_id.id == location['id'] and ((not str(inv.invoice_date) == report_date and inv.id not in old_inv_ids) or inv.type == 'out_refund'):
                    old_inv_ids.append(inv.id)
                    old_invoice = self.env['account.move'].search_read([('id','=',inv.id)])[0]
                    invoices.append(old_invoice)

        for inv in invoices:
            inv_obj= self.env['account.move'].browse(inv['id'])
    
            if not inv['name'] == '/':
                inv['num'] = int(inv['name'].split('/')[-1])
            inv_widgets = self.env['account.move'].search([('name','=',inv['name'])]).get_widget_detail()
            inv['credit'] = [] #contains the credit
            inv['bills'] = inv_widgets #contains all payments

            inv['down'] = False #will stay a boolean
            inv['down_payment'] = False #will contain the array of down payments

            dates = []
            if len(inv_widgets) > 1:
                dates.append(inv_widgets[0]['date'])

            for cred in inv_widgets:
                if (len(dates) >= 1 and cred['date'] not in dates):
                    inv['down'] = True
                if cred['account_payment_id']:
                    account = self.env['account.payment'].search([('id','=',cred['account_payment_id'])])
                    cred['payment_method'] = [account.details, account.l10n_mx_edi_payment_method_id.name]
                    cred['record_name'] = account.name
                else: # if it contains a reverse payment
                    cred['record_name'] = cred['ref'].split(' ')[0] 
                    cred['payment_method'] = False
                    inv['credit'].append(cred)

            if inv_obj.amount_residual < inv_obj.amount_total and inv_obj.amount_residual > 0:
                inv['down'] = True
            if not str(inv_obj.invoice_date) == report_date:
                inv['down'] =True 

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'request': self,
            'location': location,
            'date': report_date,
            'invoices': invoices or None,
            'last_invoice': last_invoice
        }