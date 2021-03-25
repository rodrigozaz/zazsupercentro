# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Partner(models.Model):
    _inherit = 'res.partner'

    type_sale = fields.Selection(string="Tipo de Venta", selection=[
        ('Subdistribuidor', 'Subdistribuidor'),
        ('Constructor', 'Constructor'),
        ('Mostrador', 'Mostrador')
        ])