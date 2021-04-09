# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, fields, models, _

class VendorPayment(models.TransientModel):
    _name = 'vendor.payment'
    _description = 'Vendor Payment Report'

    vendor_id = fields.Many2one('res.partner', string= 'Proveedor',required=True,) #vendor
    payment_date = fields.Date(string="Fecha de pago",required=True,)  #payment Date

    def print_pdf_payment(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'vendor_id': self.vendor_id.id,
                'date':self.payment_date
            },
        }
        return self.env.ref('materiales_payment_report.action_vendor_payment_materiales').report_action(self, data=data)

class ReportAttendanceRecap(models.AbstractModel):

    _name = 'report.materiales_payment_report.vendor_payment_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        vendor_id = data['form']['vendor_id']
        date = data['form']['date']


        vendor = self.env['res.partner'].search([('id','=', vendor_id)])
        payments = self.env['account.payment'].search([('partner_id','=',vendor_id),('payment_date','=',date),('payment_type','=','outbound'),('state','in',['draft','posted'])])


        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date': date,
            'vendor':vendor.name,
            'payments': payments
        }