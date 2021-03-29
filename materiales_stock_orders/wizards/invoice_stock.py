# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, fields, models, _
import json
import io
from datetime import datetime
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

import logging

_logger = logging.getLogger(__name__)
# _logger.info()
class VendorPayment(models.TransientModel):
    _name = 'stock.invoice.report'
    _description = 'Invoice Stock Report'

    warehouse_id = fields.Many2one('stock.warehouse', string= 'Warehouse',required=True,)
    start_date = fields.Date(string="Start Date",required=True,)  
    end_date = fields.Date(string="End Date",required=True,) 

    def print_pdf_invoice_stock(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'warehouse': self.warehouse_id.id,
                'start_date':self.start_date,
                'end_date':self.end_date,
            },
        }
        return self.env.ref('materiales_stock_orders.action_stock_invoice_report_materiales').report_action(self, data=data)

    def export_xls(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'warehouse': self.warehouse_id.id,
                'start_date':self.start_date,
                'end_date':self.end_date,
            },
        }

        
        return {
            'type': 'ir_actions_xlsx_download',
            'data': {'model': 'stock.invoice.report',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': '{0}_invoice_stock'.format(self.warehouse_id.name),
                     }
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        cell_format = workbook.add_format({'font_size': '10px', 'bold': True,})
        head = workbook.add_format({'align': 'center', 'bold': True,'font_size':'16px'})
        title = workbook.add_format({'align': 'center', 'bold': True,'font_size':'12px'})
        txt = workbook.add_format({'font_size': '10px'})
        # sheet.merge_range('A1:G2', 'Reporte de Existencias', head)


        data_info = self.env['report.materiales_stock_orders.invoice_stock_report']._get_report_values(docids=None, data=data)
        # warehouse = self.env['stock.warehouse'].search([('id','=',data['warehouse'])])
        # print(data_info,'\n\n\n')

        # sheet.merge_range('A3:G3', warehouse.name, title)
        # sheet.write(3,1, 'Fecha:', cell_format)
        # sheet.merge_range('C4:D4', data['reportdate'],txt)

        sheet.write(0,0, 'Fecha de Factura', cell_format)
        sheet.write(0,1, 'Factura', cell_format)
        sheet.write(0,2, 'Tipo de Venta', cell_format)
        sheet.write(0,3, 'Salesperson', cell_format)
        sheet.write(0,4, 'Convenio de Venta', cell_format)
        sheet.write(0,5, 'Codigo SN', cell_format)
        sheet.write(0,6, 'Cliente', cell_format)
        sheet.write(0,7,'Codigo', cell_format)
        sheet.write(0,8, 'Producto', cell_format)
        sheet.write(0,9, 'UdM', cell_format)
        sheet.write(0,10, 'Cantidad Pedida', cell_format)
        sheet.write(0,11, 'Pendiente de Entregar', cell_format)
        sheet.write(0,12, 'Precio Unitario con Descuento', cell_format)
        sheet.write(0,13, 'Monto por Entregar', cell_format)

        row = 1

        for inv in data_info['invoices']:
            sheet.write(row,0, datetime.strftime(inv['invoice_date'], '%Y-%m-%d'), txt)
            sheet.write(row,1, inv['invoice_name'], txt)
            sheet.write(row,2, inv['invoice_tipo'], txt)
            sheet.write(row,3, inv['invoice_salesperson'], txt)
            sheet.write(row,4, inv['agreement'], txt)
            sheet.write(row,5, inv['invoice_ref'], txt)
            sheet.write(row,6, inv['invoice_cust'], txt)
            sheet.write(row,7, inv['product_num'], txt)
            sheet.write(row,8,inv['product_name'], txt)
            sheet.write(row,9, inv['product_uom'], txt)
            sheet.write(row,10, inv['product_ordered'], txt)
            sheet.write(row,11, inv['product_deliver'], txt)
            sheet.write(row,12, inv['unit_price'], txt)
            sheet.write(row,13, inv['total_price'], txt)
            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

class ReportAttendanceRecap(models.AbstractModel):

    _name = 'report.materiales_stock_orders.invoice_stock_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        warehouse_id = data['form']['warehouse']
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']

        warehouse = self.env['stock.warehouse'].browse(warehouse_id)
        invoices = self.env['account.move'].search([('invoice_date','>=',start_date),('invoice_date','<=',end_date),('warehouse_id','=',warehouse.id)])
        invoice_stock = []

        for inv in invoices:
            if inv.invoice_origin:
                for line in inv.invoice_line_ids:
                    if line.sale_line_ids and line.sale_line_ids.qty_delivered < line.sale_line_ids.product_uom_qty:
                        deliver_amt = line.quantity - line.sale_line_ids.qty_delivered
                        invoice_stock.append({
                            'invoice_date': inv.invoice_date,
                            'invoice_name': inv.name,
                            'invoice_tipo': inv.type_sale,
                            'invoice_salesperson': inv.invoice_user_id.name,
                            'agreement': line.sale_line_ids.order_id.agreement_id.name or '',
                            'invoice_ref': inv.ref,
                            'invoice_cust': inv.partner_id.name,
                            'product_num': line.product_id.default_code,
                            'product_name': line.product_id.name,
                            'product_uom': line.product_uom_id.name,
                            'product_ordered':line.quantity,
                            'product_deliver': deliver_amt,
                            'unit_price': line.price_unit,
                            'total_price': line.price_unit * deliver_amt
                        })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'start_date':start_date,
            'end_date': end_date,
            'warehouse':warehouse_id,
            'invoices': invoice_stock
        }


