# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    type_sale = fields.Selection(string="Tipo de Venta", selection=[
        ('Subdistribuidor', 'Subdistribuidor'),
        ('Constructor', 'Constructor'),
        ('Mostrador', 'Mostrador')
        ], 	related="partner_id.type_sale")