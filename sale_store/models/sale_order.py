# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # store_id = fields.Many2one(comodel_name='sale.store')

    @api.onchange('user_id')
    def onchange_user_id(self):
        super(SaleOrder, self).onchange_user_id()
        if self.user_id and self.user_id.warehouse_ids:
            self.warehouse_id = self.user_id.warehouse_ids[0]

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.warehouse_id:
            res.update({'warehouse_id': self.warehouse_id.id})
        return res