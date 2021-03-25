# -*- coding: utf-8 -*-

from odoo import models, fields


class PricelistAgreement(models.Model):
    _inherit = "res.partner"

    agreement_id = fields.Many2many(
        'product.pricelist',
        string="Agreements"
    )
