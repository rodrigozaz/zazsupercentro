# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Picking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        self.ensure_one()
        if self.picking_type_code == 'incoming':
            move_lines = self.move_lines or self.move_ids_without_package
            for line in move_lines:
                if line.quantity_done > line.product_uom_qty:
                    raise ValidationError('You cannot receive more than the ordered quantity. Please, enter another quantity')
        res = super(Picking,self).button_validate()
        return res 
        