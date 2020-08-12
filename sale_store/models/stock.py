# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    purchase_seq_id = fields.Many2one(comodel_name='ir.sequence', string='Purchase Order Sequence',
                                      default=lambda self: self.env.ref('purchase.seq_purchase_order'))
    sale_seq_id = fields.Many2one(comodel_name='ir.sequence', string='Sale Order Sequence',
                                      default=lambda self: self.env.ref('sale.seq_sale_order'))
    cust_in_pay_seq_id = fields.Many2one(comodel_name='ir.sequence', string='Receive Customer Payment Sequence',
                                      default=lambda self: self.env.ref('account.sequence_payment_customer_invoice'))
    cust_out_pay_seq_id = fields.Many2one(comodel_name='ir.sequence', string='Send customer Payment Sequence',
                                      default=lambda self: self.env.ref('account.sequence_payment_customer_refund'))
    supp_in_pay_seq_id = fields.Many2one(comodel_name='ir.sequence', string='Receive Supplier Payment Sequence',
                                         default=lambda self: self.env.ref('account.sequence_payment_supplier_refund'))
    supp_out_pay_seq_id = fields.Many2one(comodel_name='ir.sequence', string='Send Supplier Payment Sequence',
                                          default=lambda self: self.env.ref('account.sequence_payment_supplier_invoice'))
