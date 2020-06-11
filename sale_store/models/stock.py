# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    purchase_seq_id = fields.Many2one(comodel_name='ir.sequence', string='Purchase Order Sequence',
                                      default=lambda self: self.env.ref('purchase.seq_purchase_order'))