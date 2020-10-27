# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime

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

class ReportAttendanceRecap(models.AbstractModel):

    _name = 'report.materiales_stock_report.detailed_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        warehouse = self.env['stock.warehouse'].search([('id','=',data['form']['warehouse'])])
        to_date = datetime.datetime.strptime(data['form']['reportdate'], '%Y-%M-%d') + datetime.timedelta(days=1)
        try:
            self.env['product.product'].invalid_cache()
        except:
            pass
        
        to_date = datetime.datetime.strftime(to_date, '%Y-%M-%d')
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