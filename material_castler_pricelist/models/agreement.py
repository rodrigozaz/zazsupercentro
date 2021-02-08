# -*- coding: utf-8 -*-

from odoo import models, fields


class PricelistAgreement(models.Model):
    _name = "pricelist.agreement"
    _description = "Pricelist Agreement"

    name = fields.Char(string="Agreement Name")
    vendor_id = fields.Many2one("res.partner", string="Vendor")
    start_date = fields.Date()
    end_date = fields.Date()
