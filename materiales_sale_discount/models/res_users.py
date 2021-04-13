# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    discount_limit = fields.Float(string='Discount Limit' )
    responsible_ids = fields.Many2many(comodel_name='res.partner', string='Possible Responsibles', domain=[('self_user_id', '!=', False)])