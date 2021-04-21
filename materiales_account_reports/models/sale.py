# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self):
        '''
        Margin and Cost computation for Invoice
        '''
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        res.update({
            'warehouse_id': self.order_id.warehouse_id.id,
            'cost_price': self.purchase_price,
        })
        return res