# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    agreement_id = fields.Many2one(
        'product.pricelist',
        string="Agreement",
        domain="[('id', 'in', agreement_ids)]",
    )
    agreement_ids = fields.Many2many(
        'product.pricelist',
        compute='_compute_agreement_ids',
        string=""
    )

    @api.depends('partner_id')
    def _compute_agreement_ids(self):
        for order in self:
            if order.partner_id:
                order.agreement_ids = order.partner_id.agreement_id
            else:
                order.agreement_ids = []

    @api.onchange('partner_id')
    def onchange_partner_pricelist(self):
        self.agreement_ids = self.partner_id.agreement_id
        self.agreement_id = False

    @api.onchange('agreement_id')
    def onchange_agreement_id(self):
        if self.agreement_id:
            self.pricelist_id = self.agreement_id
