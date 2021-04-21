# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    warehouse_id = fields.Many2one(comodel_name='stock.warehouse',
                            string='Warehouse', readonly=True)
    margin_percent = fields.Float('Margin (%)', compute='_compute_cost_margin', store=True,
                            help='The margin (%) on a sales computed using margin amount in invoice currency.')
    margin = fields.Monetary(string='Margin Amount', compute='_compute_cost_margin',
                            store=True, currency_field='always_set_currency_id')
    cost_price = fields.Monetary(string='Unit Cost', digits='Product Price',
                            currency_field='always_set_currency_id')
    cost_subtotal = fields.Monetary(string='Total Cost', store=True, readonly=True,
                            currency_field='always_set_currency_id')
    discount_price_unit = fields.Float(string='Discounted Unit Price', digits='Product Price',
                            compute='_compute_cost_margin', store=True,)
    type_sale = fields.Selection(string='Tipo de Venta', selection=[
                                ('Subdistribuidor', 'Subdistribuidor'),
                                ('Constructor', 'Constructor'),
                                ('Mostrador', 'Mostrador')
                                ], related='move_id.partner_id.type_sale',
                            store=True, readonly=True)

    @api.depends('price_subtotal', 'quantity', 'cost_price', 'price_unit', 'discount')
    def _compute_cost_margin(self):
        for line in self:
            line.margin = line.price_subtotal - (line.cost_price * line.quantity)
            line.margin_percent =  (line.margin/line.price_subtotal) * 100.0 if line.price_subtotal else 0.0
            line.discount_price_unit = line.price_unit * (1-((line.discount or 0.0) / 100.0))
            line.cost_subtotal = line.cost_price * line.quantity