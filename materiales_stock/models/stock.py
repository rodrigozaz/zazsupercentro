# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Picking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        self.ensure_one()
        move_lines = self.move_lines or self.move_ids_without_package
        for line in move_lines:
            if line.quantity_done > line.product_uom_qty:
                if line.picking_id.picking_type_code == 'incoming':
                    raise ValidationError(_('You cannot receive more than the ordered quantity. Please, enter another quantity'))
                if line.picking_id.picking_type_code == 'outgoing':
                    raise ValidationError(_('You cannot deliver more than the ordered quantity. Please, enter another quantity'))            
        res = super(Picking,self).button_validate()
        return res 
        