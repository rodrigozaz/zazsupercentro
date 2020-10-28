# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime

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