# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    state = fields.Selection(selection_add=[('to_approve', 'Pending Approval')])
    responsible = fields.Many2one('res.partner', string='Responsible', domain="[('self_user_id', '!=', False),('groups_id','=',31)]")
    show_request = fields.Boolean(string='Request Approval?', default=False, compute='_compute_show_request')
    show_authorization = fields.Boolean(string='Authorized?', default=False, compute='_compute_show_authorization')
    approve = fields.Boolean(string='Approved?', default=False)
    under_limit = fields.Boolean(string='Under Limit?', default=True)

    def action_confirm(self):
        self.flush()
        for so in self:
            if so.under_limit == False and so.approve == False:
                raise ValidationError(_("Cannot confirm without Responsible's approval"))
        return super(SaleOrder, self).action_confirm()

    def button_request(self):
        self.flush()
        for so in self:
            if so.under_limit == True:
                raise ValidationError(_("You do not need the Responsible's approval"))
            template_id = self.env.ref('materiales_sale_discount.discount_approval_email')
            if so.responsible.email:
                email = '"{}" <{}>'.format(so.responsible.name, so.responsible.email)
                template_id.send_mail(so.id, email_values={'email_to': email}, force_send=False)
                so.write({
                    'state': 'to_approve'
                })
            else:
                raise UserError(_("There is no responsible or responsible email assigned"))

    def button_approve(self):
        for so in self:
            template_id = self.env.ref('materiales_sale_discount.request_approved_email')
            if so.user_id.email:
                email = '"{}" <{}>'.format(so.user_id.name, so.user_id.email)
                template_id.send_mail(so.id, email_values={'email_to': email}, force_send=False)
                so.write({
                    'state': 'draft',
                    'approve': True
                })
            else:
                raise UserError(_("There is no Salesperson or Salesperson email assigned"))

    def button_reject(self):
        for so in self:
            template_id = self.env.ref('materiales_sale_discount.request_denied_email')
            if so.user_id.email:
                email = '"{}" <{}>'.format(so.user_id.name, so.user_id.email)
                template_id.send_mail(so.id, email_values={'email_to': email}, force_send=False)
                so.write({
                    'state': 'draft',
                    'approve': False
                })
            else:
                raise UserError(_("There is no Salesperson or Salesperson email assigned"))

    @api.depends('responsible')
    def _compute_show_authorization(self):
        for so in self:
            if self.env.user == so.responsible.self_user_id:
                so.show_authorization = True
            else:
                so.show_authorization = False

    @api.depends('order_line', 'show_authorization')
    def _compute_show_request(self):
        for so in self:
            so.show_request = False
            under_limit = True
            if so.show_authorization:
                so.show_request = False
                under_limit = so.under_limit
            else:
                for line in so.order_line:
                    if line.past_limit == True:
                        so.show_request = True
                        under_limit = False
            so.write({
                'under_limit': under_limit
            })

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    past_limit = fields.Boolean(string='Is Discount Past Limit?', default=False)

    @api.onchange('discount')
    def subtotal_change(self):
        for line in self:
            if line.discount > self.env.user.discount_limit*100:
                line.past_limit = True
            else:
                line.past_limit = False


