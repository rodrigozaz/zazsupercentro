# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    location_ids = fields.Many2many(string='Locations within allowed warehouses', comodel_name='stock.location', compute='compute_location_ids', store=True)
    
    @api.depends('warehouse_ids')
    def compute_location_ids(self):
        locations = []
        for warehouse in self.warehouse_ids:
            locations += self.env['stock.location'].search([('warehouse_id', '=', warehouse.id)]).ids
        self.location_ids = locations
