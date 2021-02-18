# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime,timedelta

class WarehouseSales(models.Model):
    _name = 'warehouse.product.stock'
    _description = 'stock report for all warehouse'

    product_id = fields.Many2one('product.product', string= 'Producto',required=True,)    

    def print_pdf_product_warehouse(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'product': self.product_id.id,
            },
        }
        return self.env.ref('materiales_sale_stock.action_product_all_warehouse').report_action(self, data=data)

class ReportAttendanceRecap(models.AbstractModel):

    _name = 'report.materiales_sale_stock.warehouse_product_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        product_id = data['form']['product']

        warehouses = self.env['stock.warehouse'].sudo().search([('company_id','=',self.env.company.id)])
        product_stocks = []

        product = self.env['product.product'].search([('id','=', product_id)])
        for wh in warehouses:
            product.invalidate_cache()
            p = product.with_context({'warehouse': wh.id})
            product_stocks.append({
                'name': wh.name,
                'available': p.qty_available,
                'reserved': p.qty_available - p.free_qty,
                'forcasted': p.virtual_available,
            })

        
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'request': self,
            'date': datetime.now().date(),
            'product':product,
            'stocks': product_stocks
        }