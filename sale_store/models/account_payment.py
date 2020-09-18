# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def post(self):
        for payment in self.filtered(lambda p: p.invoice_ids):
            if len(p.invoice_ids.mapped('journal_id')) > 1:
                raise UserError(_("Can not register payment for invoices having different Journals."))
            journal = p.invoice_ids.mapped('journal_id')
            if not payment.name and journal.warehouse_id:
                seq_field = False
                if payment.partner_type == 'customer':
                    if payment.payment_type == 'inbound':
                        seq_field = 'cust_in_pay_seq_id'
                    if payment.payment_type == 'outbound':
                        seq_field = 'cust_out_pay_seq_id'
                if payment.partner_type == 'supplier':
                    if payment.payment_type == 'inbound':
                        seq_field = 'supp_out_pay_seq_id'
                    if payment.payment_type == 'outbound':
                        seq_field = 'supp_in_pay_seq_id'
                if seq_field and getattr(journal.warehouse_id, seq_field):
                    sequence = journal.warehouse_id[seq_field]
                    payment.name = sequence.next_by_id(sequence_date=payment.payment_date)
        return super(AccountPayment, self).post()

