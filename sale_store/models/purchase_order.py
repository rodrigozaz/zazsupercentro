# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    warehouse_id = fields.Many2one(related='picking_type_id.warehouse_id', string='Receiving Warehouse')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New' and vals.get('picking_type_id'):
            picking_type = self.env['stock.picking.type'].browse(vals.get('picking_type_id'))
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            if picking_type.exists() and picking_type.warehouse_id and picking_type.warehouse_id.purchase_seq_id:
                vals['name'] = picking_type.warehouse_id.purchase_seq_id.next_by_id(sequence_date=seq_date)
        return super(PurchaseOrder, self).create(vals)