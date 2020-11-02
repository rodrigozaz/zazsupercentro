# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
import json
import io
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class DetailedInventory(models.Model):
    _name = 'detailed.inventory'
    _description = 'Detailed Inventory Report'

    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    warehouse_ids = fields.Many2many('stock.warehouse', compute="_compute_warehouses")
    warehouse_id = fields.Many2one('stock.warehouse', translate=True, string='Sucursal',required=True,)    
    report_date = fields.Date(string='Fecha',translate=True, required=True)

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
                'reportdate': self.report_date,
            },
        }
        return self.env.ref('materiales_stock_report.action_detailed_stock').report_action(self, data=data)

    def export_xls(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'warehouse': self.warehouse_id.id,
            'reportdate': self.report_date,
        }
        return {
            'type': 'ir_actions_xlsx_download',
            'data': {'model': 'detailed.inventory',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Reporte de Existencias',
                     }
        }

    def get_lines(self,data, warehouse):
        to_date = datetime.datetime.strptime(data['reportdate'], '%Y-%m-%d') + datetime.timedelta(days=2)
        try:
            self.env['product.product'].invalid_cache()
        except:
            pass
        
        to_date = datetime.datetime.strftime(to_date, '%Y-%m-%d')
        products = self.env['product.product'].search([]).with_context({'from_date': data['reportdate'], 'to_date': to_date, 'warehouse': warehouse.id})
        lines = []

        for prod in products:
            if prod.qty_available > 0:
                product = {
                    'product': prod.name,
                    'code': prod.default_code,
                    'uom': prod.uom_name,
                    'qty_hand': prod.qty_available,
                    'reserved': prod.qty_available - prod.free_qty,
                    'ordered': prod.incoming_qty,
                    'price': prod.standard_price,
                    'forecasted': prod.incoming_qty + prod.free_qty,
                    'value': prod.standard_price * prod.qty_available
                }
                lines.append(product)
        return lines


    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        cell_format = workbook.add_format({'font_size': '10px', 'bold': True,})
        head = workbook.add_format({'align': 'center', 'bold': True,'font_size':'16px'})
        title = workbook.add_format({'align': 'center', 'bold': True,'font_size':'12px'})
        txt = workbook.add_format({'font_size': '10px'})
        sheet.merge_range('A1:G2', 'Reporte de Existencias', head)

        warehouse = self.env['stock.warehouse'].search([('id','=',data['warehouse'])])

        stocks = self.get_lines(data,warehouse)

        sheet.merge_range('A3:G3', warehouse.name, title)
        sheet.write(3,1, 'Fecha:', cell_format)
        sheet.merge_range('C4:D4', data['reportdate'],txt)

        sheet.write(5,0, 'Codigo', cell_format)
        sheet.write(5,1, 'Producto', cell_format)
        sheet.write(5,2, 'U.M.', cell_format)
        sheet.write(5,3, 'Inventario en Stock', cell_format)
        sheet.write(5,4, 'Comprometido', cell_format)
        sheet.write(5,5, 'Pedido', cell_format)
        sheet.write(5,6,'Disponible', cell_format)
        sheet.write(5,7, 'Costo', cell_format)
        sheet.write(5,8, 'Valor del Inventario', cell_format)

        row = 6

        for stock in stocks:
            sheet.write(row,0, stock['code'], txt)
            sheet.write(row,1, stock['product'], txt)
            sheet.write(row,2, stock['uom'], txt)
            sheet.write(row,3, stock['qty_hand'], txt)
            sheet.write(row,4, stock['reserved'], txt)
            sheet.write(row,5, stock['ordered'], txt)
            sheet.write(row,6, stock['forecasted'], txt)
            sheet.write(row,7,stock['price'], txt)
            sheet.write(row,8, stock['value'], txt)
            row += 1
            
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()


class ReportAttendanceRecap(models.AbstractModel):

    _name = 'report.materiales_stock_report.detailed_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        warehouse = self.env['stock.warehouse'].search([('id','=',data['form']['warehouse'])])
        to_date = datetime.datetime.strptime(data['form']['reportdate'], '%Y-%m-%d') + datetime.timedelta(days=2)
        try:
            self.env['product.product'].invalid_cache()
        except:
            pass
        
        to_date = datetime.datetime.strftime(to_date, '%Y-%m-%d')
        products = self.env['product.product'].search([]).with_context({'from_date': data['form']['reportdate'], 'to_date': to_date, 'warehouse': warehouse.id})
        
        inventory = []
        for prod in products:
            if prod.qty_available > 0:
                product = {}
                product['product'] = prod.name
                product['code'] = prod.default_code
                product['uom'] = prod.uom_name
                product['qty_hand'] = prod.qty_available
                product['reserved'] = prod.qty_available - prod.free_qty
                product['ordered'] = prod.incoming_qty
                product['price'] = prod.standard_price
                product['forecasted'] = product['qty_hand'] - product['reserved'] + product['ordered']
                inventory.append(product)

        return{
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'data': data['form'],
            'warehouse':warehouse[0]['display_name'],
            'products': inventory
        }
# lot_stock_id
# .with_context({'date': data['form']['warehouse']})