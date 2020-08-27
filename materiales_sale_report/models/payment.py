# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Payment(models.Model):
    _inherit = 'account.payment'

    details = fields.Char(string="Payment Detail")

    