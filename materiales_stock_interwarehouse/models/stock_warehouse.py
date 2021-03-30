# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError

class StockWerehouse(models.Model):
    _inherit = 'stock.warehouse'

    def check_access_rule(self, operation):
        """
        Add Access for interwarehosue read access :
            - read:
                - allow reading source warehouse for picking
        """
        ret = None
        try: 
            ret = super(StockWerehouse, self).check_access_rule(operation=operation)
        except AccessError as ae:
            if operation == 'read':
                # params = self._context.get('params')
                # model = self._context.get('params').get('model', False)
                # record_id = self._context.get('params').get('id', False)
                
                # TODO: if record_id and model == 'stock.picking' and 
                #      add group this user can by pass warehosue picking
                # if record_id and model == 'stock.picking' :
                return
            raise ae
        return ret