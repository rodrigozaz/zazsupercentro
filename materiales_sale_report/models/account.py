# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Payment(models.Model):
    _inherit = 'account.move'

    def get_widget_detail(self):
        return self._get_reconciled_info_JSON_values()

