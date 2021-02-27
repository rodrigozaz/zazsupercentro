# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _

import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection(selection_add=[('to_approve', 'Pending Approval')])
    show_request = fields.Boolean(string='Show Request Transfer Button?', compute='_compute_show_request', default=True, store=True)

    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        check_company=True, readonly=True, required=True,
        states={'draft': [('readonly', False)]}, domain=lambda self: [('id', 'in', self.env.user.location_ids.ids)])

    def button_request(self):
        for picking in self:
            template_id = self.env.ref('materiales_stock_interwarehouse.transfer_request_email')
            admins = picking.env['res.users'].search(['&',('location_ids', 'in', [picking.location_id.id]),('groups_id','=', 20)])
            if admins:
                for admin in admins:
                    email = '"{}" <{}>'.format(admin.name, admin.login)
                    template_id.send_mail(picking.id, email_values={'email_to': email}, force_send=False)
                picking.write({
                    'state': 'to_approve'
                })
            else:
                raise UserError(_("There is no admin assigned to the origin location"))

    @api.depends('state', 'is_locked')
    def _compute_show_validate(self):
        for picking in self:
            if not (picking.immediate_transfer) and picking.state == 'draft':
                picking.show_validate = False
            elif picking.picking_type_id.sequence_code == 'INT' and picking.state == 'to_approve' and picking.location_id.id in self.env.user.location_ids.ids and 20 in self.env.user.groups_id.ids:
                picking.show_validate = True
            elif picking.picking_type_id.sequence_code == 'INT' and picking.state in ['draft', 'assigned', 'waiting', 'to_approve']:
                picking.show_validate = False
            elif picking.state not in ('draft', 'waiting', 'confirmed', 'assigned', 'to_approve') or not picking.is_locked:
                picking.show_validate = False
            else:
                picking.show_validate = True

    @api.depends('state', 'location_dest_id')
    def _compute_show_request(self):
        for picking in self:
            if picking.state in ['draft', 'waiting', 'assigned'] and picking.location_dest_id.id in self.env.user.location_ids.ids and picking.picking_type_id.sequence_code == 'INT':
                picking.show_request = True
            else:
                picking.show_request = False