# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', compute='compute_warehouse_id', store=True)

    @api.depends('location_id')
    def compute_warehouse_id(self):
        for location in self:
            location.warehouse_id = location.get_warehouse()