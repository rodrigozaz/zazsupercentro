# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # store_id = fields.Many2one(comodel_name='sale.store')

    @api.model
    def create(self, vals):
        if vals.get('namd', _('New')) == _('New') and vals.get('warehouse_id'):
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            warehouse = self.env['stock.warehouse'].browse(vals['warehouse_id'])
            if warehouse and warehouse.sale_seq_id:
                vals['name'] = warehouse.sale_seq_id.next_by_id(sequence_date=seq_date) or _('New')
        return super(SaleOrder, self).create(vals)
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