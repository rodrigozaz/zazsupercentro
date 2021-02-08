# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    start_date = fields.Date()
    end_date = fields.Date()


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    agreement_id = fields.Many2one("pricelist.agreement", string="Agreement")

    @api.onchange('agreement_id')
    def onchange_agreement_id(self):
        for record in self:
            agreement_id = record.agreement_id
            record.date_start = agreement_id.start_date
            record.date_end = agreement_id.end_date
