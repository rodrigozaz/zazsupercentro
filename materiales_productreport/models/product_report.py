# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import json
import io
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class ProductInventory(models.Model):
    _name = 'product.inventory'
    _description = 'Product Inventory'

    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    warehouse_ids = fields.Many2many('stock.warehouse', compute="_compute_warehouses")
    warehouse_id = fields.Many2one('stock.warehouse', string='Sucursal',required=True,)
    product_id = fields.Many2one('product.product', string="Producto", required=True)   
    start_date = fields.Date(string='Fecha inicial',required=True)
    end_date = fields.Date(string='Fecha Final',required=True)

    @api.depends('user_id')
    def _compute_warehouses(self):
        for rec in self:
            rec.warehouse_ids = rec.user_id.warehouse_ids

    def print_pdf_product_inventory(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'warehouse': self.warehouse_id.id,
                'product': self.product_id.id,
                'start_date': self.start_date,
                'end_date': self.end_date
            },
        }
        return self.env.ref('materiales_productreport.action_product_report').report_action(self, data=data)

    def export_xls(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'warehouse': self.warehouse_id.id,
            'product': self.product_id.id,
            'start_date': self.start_date,
            'end_date': self.end_date

        }
        return {
            'type': 'ir_actions_xlsx_download',
            'data': {'model': 'product.inventory',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Kardex de Producto',
                     }
        }

    def get_lines(self, data, warehouse,product):

        lines = []
        stocks = self.env['stock.move'].search([('warehouse_id','=',warehouse.id),('product_id','=',product.id),('date','>=',data['start_date']),('date','<=',data['end_date'])])
        total = 0
        for stock in stocks:
            cost = 0
            if stock.sale_line_id:
                cost = stock.sale_line_id.price_unit
            else:
                cost = stock.price_unit

            if stock.picking_code == 'incoming':
                total += stock.quantity_done
            elif stock.picking_code == 'outgoing':
                total -= stock.quantity_done
            vals = {
                'date': datetime.strftime(stock.date, '%Y-%m-%d'),
                'name': stock.picking_id.name,
                'quantity': int(stock.quantity_done),
                'cost': cost,
                'total': int(total),
                'comment': 'Basado en '+ stock.origin
            }
            lines.append(vals)
        return lines

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        cell_format = workbook.add_format({'font_size': '10px', 'bold': True,})
        head = workbook.add_format({'align': 'center', 'bold': True,'font_size':'16px'})
        title = workbook.add_format({'align': 'center', 'bold': True,'font_size':'12px'})
        txt = workbook.add_format({'font_size': '10px'})
        sheet.merge_range('A1:G2', 'Kardex de Producto', head)

        warehouse = self.env['stock.warehouse'].search([('id','=',data['warehouse'])])
        product = self.env['product.product'].search([('id','=', data['product'])]).with_context({'warehouse': warehouse.id})

        stocks = self.get_lines(data,warehouse,product)

        sheet.merge_range('A3:G3', warehouse.name, title)
        sheet.merge_range('A4:G4', product.name, title)
        date = data['start_date'] + ' - ' + data['end_date']
        sheet.write(4,1, 'Fecha:', cell_format)
        sheet.merge_range('C5:E5', date,txt)

        sheet.write(6,0, 'Fecha', cell_format)
        sheet.write(6,1, 'Documento', cell_format)
        sheet.write(6,2, 'Cantidad', cell_format)
        sheet.write(6,3, 'Cost', cell_format)
        sheet.write(6,4, 'Saldo', cell_format)
        sheet.write(6,5, 'Comentarios', cell_format)

        row = 7
        for stock in stocks:
            sheet.write(row,0, stock['date'], txt)
            sheet.write(row,1, stock['name'], txt)
            sheet.write(row,2, stock['quantity'], txt)
            sheet.write(row,3, stock['cost'], txt)
            sheet.write(row,4, stock['total'], txt)
            sheet.write(row,5, stock['comment'], txt)
            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

class ReportAttendanceRecap(models.AbstractModel):
    
    _name = 'report.materiales_productreport.product_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        location_id = data['form']['warehouse']
        product_id = data['form']['product']
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']

        warehouse = self.env['stock.warehouse'].search([('id','=',location_id)])
        product = self.env['product.product'].search([('id','=', product_id)]).with_context({'warehouse': warehouse.id})

        stocks = self.env['stock.move'].search([('warehouse_id','=',warehouse.id),('product_id','=',product.id),('date','>=',start_date),('date','<=',end_date)])

        print(stocks)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'warehouse': warehouse[0]['display_name'],
            'start_date':start_date,
            'end_date' : end_date,
            'stocks': stocks,
            'product' : product
        }