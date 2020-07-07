# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.constrains('qty_done')
    def _validate_quantity(self):
        for record in self:
            if record.qty_done > record.move_id.product_uom_qty:
                raise ValidationError(_('You cannot receive more than the ordered quantity. Please, enter another quantity'))