# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    agreement_id = fields.Many2one("pricelist.agreement", string="Agreement")


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange('product_id')
    def onchange_prod_price(self):
        agreement = self.order_id.agreement_id
        product = self.product_id
        product._prepare_sellers()

    #     if product and product.seller_ids and agreement:
    #         supp_info = product.seller_ids.filtered(lambda s: s.agreement_id == agreement)
    #         print("supp_info.price.........", supp_info)
    #         self.price_unit = supp_info.price


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _prepare_sellers(self, params=False):
        print("_prepare_sellers.......", self)
        if params:
            agreement = params.get('order_id').agreement_id
            print("_prepare_sellers..params.....", params.get('order_id').agreement_id)
            return self.env['product.supplierinfo'].search([('product_tmpl_id', '=', self.product_tmpl_id.id),
                                                            ('name.active', '=', True),
                                                            ('agreement_id', '=', agreement.id)]).sorted(lambda s: (s.sequence, -s.min_qty, s.price, s.id))
