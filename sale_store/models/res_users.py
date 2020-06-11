# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    warehouse_ids = fields.Many2many(string='Allowed Warehouse', comodel_name='stock.warehouse')