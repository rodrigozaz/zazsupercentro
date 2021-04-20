# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime,timedelta
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

        company_id = self.env.context.get('force_company', self.env.company.id)
        create_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        domain = [
            ('product_id', '=', product.id),
            ('company_id', '=', company_id),
            ('create_date', '<=', create_date),
            '|',
            ('stock_move_id.location_id','=', warehouse.lot_stock_id.id),
            ('stock_move_id.location_dest_id','=', warehouse.lot_stock_id.id),
        ]
        
        groups = self.env['stock.valuation.layer'].with_context({'warehouse': warehouse.id}).read_group(domain, ['unit_cost','value:sum', 'quantity:sum'], ['product_id'])
        total_val = 0
        for group in groups:
            total_val = self.env.company.currency_id.round(group['value'])

        stocks = self.env['stock.move'].search([('state', 'in', ['done']),'|',('location_dest_id','=',warehouse.lot_stock_id.id),('location_id','=',warehouse.lot_stock_id.id),('product_id','=',product.id),('date','>=',data['start_date']),('date','<=',data['end_date'])], order="date ASC")
        total = product.qty_available
        for stock in stocks:
            cost = 0
            comment = ''
            if stock.origin:
                comment = 'Basado en '+ stock.origin

            if stock.sale_line_id:
                cost = stock.stock_valuation_layer_ids[0].unit_cost
                
            elif stock.purchase_line_id:
                cost = stock.purchase_line_id.price_unit
            else:
                cost = stock.product_id.standard_price

            if stock.picking_code == 'incoming':
                total += stock.quantity_done
                total_val += stock.stock_valuation_layer_ids[0].value
            elif stock.picking_code == 'outgoing':
                total -= stock.quantity_done
                total_val += stock.stock_valuation_layer_ids[0].value
            else:
                if stock.location_id.id == warehouse.lot_stock_id.id:
                    total -= stock.quantity_done
                    total_val -= (stock.product_id.standard_price * stock.quantity_done)
                else:
                    total += stock.quantity_done
                    total_val += (stock.product_id.standard_price * stock.quantity_done)
            vals = {
                'date': datetime.strftime(stock.date, '%Y-%m-%d'),
                'name': stock.picking_id.name,
                'quantity': int(stock.quantity_done),
                'cost': cost,
                'total': int(total),
                'total_val' : total_val,
                'comment': comment
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
        product = self.env['product.product'].search([('id','=', data['product'])]).with_context({'to_date': data['start_date'],'warehouse': warehouse.id})

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
        sheet.write(6,5, 'Valor del Inventorio', cell_format)
        sheet.write(6,6, 'Comentarios', cell_format)

        row = 7
        for stock in stocks:
            sheet.write(row,0, stock['date'], txt)
            sheet.write(row,1, stock['name'], txt)
            sheet.write(row,2, stock['quantity'], txt)
            sheet.write(row,3, stock['cost'], txt)
            sheet.write(row,4, stock['total'], txt)
            sheet.write(row,5, stock['total_val'], txt)
            sheet.write(row,6, stock['comment'], txt)
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

        product = self.env['product.product'].search([('id','=', product_id)]).with_context({'to_date': start_date,'warehouse': warehouse.id})

        stocks = self.env['stock.move'].search([('state', 'in', ['done']),'|',('location_dest_id','=',warehouse.lot_stock_id.id),('location_id','=',warehouse.lot_stock_id.id),('product_id','=',product.id),('date','>=',start_date),('date','<=',end_date)],order="date ASC")
        company_id = self.env.context.get('force_company', self.env.company.id)
        create_date = datetime.strptime(start_date, '%Y-%m-%d')
        domain = [
            ('product_id', '=', product.id),
            ('company_id', '=', company_id),
            ('create_date', '<=', create_date),
            '|',
            ('stock_move_id.location_id','=', warehouse.lot_stock_id.id),
            ('stock_move_id.location_dest_id','=', warehouse.lot_stock_id.id),
        ]
        
        groups = self.env['stock.valuation.layer'].with_context({'warehouse': warehouse.id}).read_group(domain, ['unit_cost','value:sum', 'quantity:sum'], ['product_id'])
        total = 0
        for group in groups:
            total = self.env.company.currency_id.round(group['value'])

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'warehouse': warehouse[0]['display_name'],
            'warehouse_id': warehouse.lot_stock_id.id,
            'start_date':start_date,
            'end_date' : end_date,
            'stocks': stocks,
            'product' : product,
            'total_price': total
        }