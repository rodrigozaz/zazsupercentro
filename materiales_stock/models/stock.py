# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Picking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super(Picking,self).button_validate()
        for record in self:
            if record.picking_type_id.name == 'Receipts':
                move_lines = record.move_lines or record.move_ids_without_package
                for line in move_lines:
                    if line.quantity_done > line.product_uom_qty:
                        raise ValidationError('You cannot receive more than the ordered quantity. Please, enter another quantity')
        return res 
        