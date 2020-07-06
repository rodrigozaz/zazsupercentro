# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.constrains('quantity_done')
    def button_validate(self):
        for record in self:
            for line in record.move_lines:
                if line.quantity_done > line.product_uom_qty:
                    raise ValidationError('You cannot receive more than the ordered quantity. Please, enter another quantity')
        res = super(Picking,self).button_validate()
        return res