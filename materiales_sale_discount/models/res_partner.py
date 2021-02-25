# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    self_user_id = fields.Many2one('res.users', string='User Record', readonly=True, compute='_compute_self_user', store=True)
    groups_id = fields.Many2many('res.groups', string='Access Groups', related='self_user_id.groups_id')

    def _compute_self_user(self):
        for partner in self:
            partner.self_user_id = self.env['res.users'].sudo().search([('partner_id', '=', partner.id)])
            