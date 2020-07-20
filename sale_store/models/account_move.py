# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string="Warehouse",
                                   help='Warehouse of the sale order from which the invoice is created.')


class AccountMove(models.Model):
    _inherit = 'account.move'

    warehouse_id = fields.Many2one(related='journal_id.warehouse_id')
