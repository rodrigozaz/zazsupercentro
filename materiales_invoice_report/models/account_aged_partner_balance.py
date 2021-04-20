# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import models, api, _, _lt, fields
from odoo.tools.misc import format_date
from dateutil.relativedelta import relativedelta
from odoo.tools import float_is_zero


class report_account_warehouse(models.AbstractModel):
    _name = "account.report.warehouse"
    _inherit = 'account.aged.partner'

    filter_analytic = True
    filter_unfold_all = False
    filter_partner = False

    def _get_columns_name(self, options):
        columns = [
            {},
            {},
            {'name': _("Customer Code"), 'class': '', 'style': 'white-space:nowrap;'},
            {'name': _("Customer Name"), 'class': '', 'style': 'white-space:nowrap;'},
            {'name': _("Total Invoiced"), 'class': '', 'style': 'white-space:nowrap;'},
            {'name': _("Total Margin ($)"), 'class': '', 'style': 'white-space:nowrap;'},
            {'name': _("Margin (%)"), 'class': '', 'style': 'white-space:nowrap;'},
        ]
        return columns

    @api.model
    def _get_lines(self, options, line_id=None):
        sign = -1.0 if self.env.context.get('aged_balance') else 1.0
        lines = []
        account_types = [self.env.context.get('account_type')]
        context = {'include_nullified_amount': True}
        if line_id and 'warehouse_' in line_id:
            warehouse_id_str = line_id.split('_')[1]
            if warehouse_id_str.isnumeric():
                warehouse_id = self.env['stock.warehouse'].browse(int(warehouse_id_str))
            else:
                warehouse_id = False
            context.update(warehouse_ids=warehouse_id)
        # if line_id and 'partner_' in line_id:
        #     # we only want to fetch data about this partner because we are expanding a line
        #     partner_id_str = line_id.split('_')[1]
        #     if partner_id_str.isnumeric():
        #         partner_id = self.env['res.partner'].browse(int(partner_id_str))
        #     else:
        #         partner_id = False
        #     context.update(partner_ids=partner_id)
        results, total, amls = self.with_context(**context)._get_warehouse_move_lines(account_types, self._context['date_to'], 'posted', 30)

        for values in results:
            vals = {
                'id': 'warehouse_%s' % (values['warehouse_id'],),
                'name': values['name'],
                'level': 2,
                'columns': [{'name': ''}] * 4 + [{'name': self.format_value(sign * v), 'no_format': sign * v}
                                                 for v in [values['direction'], values['4'],
                                                           values['3'], values['2'],
                                                           values['1'], values['0'], values['total']]],
                'trust': values['trust'],
                'unfoldable': True,
                'unfolded': 'warehouse_%s' % (values['warehouse_id'],) in options.get('unfolded_lines'),
                'warehouse_id': values['warehouse_id'],
            }
            lines.append(vals)
            if 'warehouse_%s' % (values['warehouse_id'],) in options.get('unfolded_lines'):
                for line in amls[values['warehouse_id']]:
                    aml = line['line']
                    if aml.move_id.is_purchase_document():
                        caret_type = 'account.invoice.in'
                    elif aml.move_id.is_sale_document():
                        caret_type = 'account.invoice.out'
                    elif aml.payment_id:
                        caret_type = 'account.payment'
                    else:
                        caret_type = 'account.move'

                    line_date = aml.date_maturity or aml.date
                    if not self._context.get('no_format'):
                        line_date = format_date(self.env, line_date)
                    vals = {
                        'id': aml.id,
                        'name': aml.move_id.name,
                        'class': 'date',
                        'caret_options': caret_type,
                        'level': 4,
                        'parent_id': 'warehouse_%s' % (values['warehouse_id'],),
                        'columns': [{'name': v} for v in [format_date(self.env, aml.date_maturity or aml.date), aml.journal_id.code, aml.account_id.display_name, format_date(self.env, aml.expected_pay_date)]] +
                                   [{'name': self.format_value(sign * v, blank_if_zero=True), 'no_format': sign * v} for v in [line['period'] == 6-i and line['amount'] or 0 for i in range(7)]],
                        'action_context': {
                            'default_type': aml.move_id.type,
                            'default_journal_id': aml.move_id.journal_id.id,
                        },
                        'title_hover': self._format_aml_name(aml.name, aml.ref, aml.move_id.name),
                    }
                    lines.append(vals)
        if total and not line_id:
            total_line = {
                'id': 0,
                'name': _('Total'),
                'class': 'total',
                'level': 2,
                'columns': [{'name': ''}] * 4 + [{'name': self.format_value(sign * v), 'no_format': sign * v} for v in [total[6], total[4], total[3], total[2], total[1], total[0], total[5]]],
            }
            lines.append(total_line)
        return lines

    def _get_warehouse_move_lines(self, account_type, date_from, target_move, period_length):
        ctx = self._context
        periods = {}
        date_from = fields.Date.from_string(date_from)
        start = date_from
        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length)
            period_name = str((5-(i+1)) * period_length + 1) + '-' + str((5-i) * period_length)
            period_stop = (start - relativedelta(days=1)).strftime('%Y-%m-%d')
            if i == 0:
                period_name = '+' + str(4 * period_length)
            periods[str(i)] = {
                'name': period_name,
                'stop': period_stop,
                'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop

        res = []
        total = []
        partner_clause = ''
        cr = self.env.cr
        user_company = self.env.company
        user_currency = user_company.currency_id
        company_ids = self._context.get('company_ids') or [user_company.id]
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']
        arg_list = (tuple(move_state), tuple(account_type), date_from,)
        if 'partner_ids' in ctx:
            if ctx['partner_ids']:
                partner_clause = 'AND (l.partner_id IN %s)'
                arg_list += (tuple(ctx['partner_ids'].ids),)
            else:
                partner_clause = 'AND l.partner_id IS NULL'
        if ctx.get('partner_categories'):
            partner_clause += 'AND (l.partner_id IN %s)'
            partner_ids = self.env['res.partner'].search([('category_id', 'in', ctx['partner_categories'].ids)]).ids
            arg_list += (tuple(partner_ids or [0]),)
        arg_list += (date_from, tuple(company_ids))
        #write a query to get the names of the warehouse
        #create a field to ref the warehouse and account.move.line
        query = '''
            SELECT DISTINCT l.warehouse_id, stock_warehouse.name AS name, UPPER(stock_warehouse.name) AS UPNAME, CASE WHEN prop.value_text IS NULL THEN 'normal' ELSE prop.value_text END AS trust
            FROM account_move_line AS l
        
         '''
        # query = '''
        #     SELECT DISTINCT l.partner_id, res_partner.name AS name, UPPER(res_partner.name) AS UPNAME, CASE WHEN prop.value_text IS NULL THEN 'normal' ELSE prop.value_text END AS trust
        #     FROM account_move_line AS l
        #       LEFT JOIN res_partner ON l.partner_id = res_partner.id
        #       LEFT JOIN ir_property prop ON (prop.res_id = 'res.partner,'||res_partner.id AND prop.name='trust' AND prop.company_id=%s),
        #       account_account, account_move am
        #     WHERE (l.account_id = account_account.id)
        #         AND (l.move_id = am.id)
        #         AND (am.state IN %s)
        #         AND (account_account.internal_type IN %s)
        #         AND (
        #                 l.reconciled IS NOT TRUE
        #                 OR EXISTS (
        #                     SELECT id FROM account_partial_reconcile where max_date > %s
        #                     AND (credit_move_id = l.id OR debit_move_id = l.id)
        #                 )
        #             )
        #             ''' + partner_clause + '''
        #         AND (l.date <= %s)
        #         AND l.company_id IN %s
        #     ORDER BY UPPER(res_partner.name)
        #     '''
        # arg_list = (self.env.company.id,) + arg_list
        # cr.execute(query, arg_list)

        # partners = cr.dictfetchall()
        # # put a total of 0
        # for i in range(7):
        #     total.append(0)

        # # Build a string like (1,2,3) for easy use in SQL query
        # partner_ids = [partner['partner_id'] for partner in partners]
        # lines = dict((partner['partner_id'], []) for partner in partners)
        # if not partner_ids:
        #     return [], [], {}

        # lines[False] = []
        # # Use one query per period and store results in history (a list variable)
        # # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        # history = []
        # for i in range(5):
        #     args_list = (tuple(move_state), tuple(account_type), tuple(partner_ids),)
        #     dates_query = '(COALESCE(l.date_maturity,l.date)'

        #     if periods[str(i)]['start'] and periods[str(i)]['stop']:
        #         dates_query += ' BETWEEN %s AND %s)'
        #         args_list += (periods[str(i)]['start'], periods[str(i)]['stop'])
        #     elif periods[str(i)]['start']:
        #         dates_query += ' >= %s)'
        #         args_list += (periods[str(i)]['start'],)
        #     else:
        #         dates_query += ' <= %s)'
        #         args_list += (periods[str(i)]['stop'],)
        #     args_list += (date_from, tuple(company_ids))

        #     query = '''SELECT l.id
        #             FROM account_move_line AS l, account_account, account_move am
        #             WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
        #                 AND (am.state IN %s)
        #                 AND (account_account.internal_type IN %s)
        #                 AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
        #                 AND ''' + dates_query + '''
        #             AND (l.date <= %s)
        #             AND l.company_id IN %s
        #             ORDER BY COALESCE(l.date_maturity, l.date)'''
        #     cr.execute(query, args_list)
        #     partners_amount = {}
        #     aml_ids = [x[0] for x in cr.fetchall()]
        #     # prefetch the fields that will be used; this avoid cache misses,
        #     # which look up the cache to determine the records to read, and has
        #     # quadratic complexity when the number of records is large...
        #     move_lines = self.env['account.move.line'].browse(aml_ids)
        #     move_lines._read(['partner_id', 'company_id', 'balance', 'matched_debit_ids', 'matched_credit_ids'])
        #     move_lines.matched_debit_ids._read(['max_date', 'company_id', 'amount'])
        #     move_lines.matched_credit_ids._read(['max_date', 'company_id', 'amount'])
        #     for line in move_lines:
        #         partner_id = line.partner_id.id or False
        #         if partner_id not in partners_amount:
        #             partners_amount[partner_id] = 0.0
        #         line_amount = line.company_id.currency_id._convert(line.balance, user_currency, user_company, date_from, round = False)
        #         if user_currency.is_zero(line_amount):
        #             continue
        #         for partial_line in line.matched_debit_ids:
        #             if partial_line.max_date <= date_from:
        #                 line_amount += partial_line.company_id.currency_id._convert(partial_line.amount, user_currency, user_company, date_from, round = False)
        #         for partial_line in line.matched_credit_ids:
        #             if partial_line.max_date <= date_from:
        #                 line_amount -= partial_line.company_id.currency_id._convert(partial_line.amount, user_currency, user_company, date_from, round = False)

        #         line_amount = user_currency.round(line_amount)
        #         if not self.env.company.currency_id.is_zero(line_amount):
        #             partners_amount[partner_id] += line_amount
        #             lines.setdefault(partner_id, [])
        #             lines[partner_id].append({
        #                 'line': line,
        #                 'amount': line_amount,
        #                 'period': i + 1,
        #                 })
        #     history.append(partners_amount)

        # # This dictionary will store the not due amount of all partners
        # undue_amounts = {}
        # query = '''SELECT l.id
        #         FROM account_move_line AS l, account_account, account_move am
        #         WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
        #             AND (am.state IN %s)
        #             AND (account_account.internal_type IN %s)
        #             AND (COALESCE(l.date_maturity,l.date) >= %s)\
        #             AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
        #         AND (l.date <= %s)
        #         AND l.company_id IN %s
        #         ORDER BY COALESCE(l.date_maturity, l.date)'''
        # cr.execute(query, (tuple(move_state), tuple(account_type), date_from, tuple(partner_ids), date_from, tuple(company_ids)))
        # aml_ids = cr.fetchall()
        # aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        # for line in self.env['account.move.line'].browse(aml_ids):
        #     partner_id = line.partner_id.id or False
        #     if partner_id not in undue_amounts:
        #         undue_amounts[partner_id] = 0.0
        #     line_amount = line.company_id.currency_id._convert(line.balance, user_currency, user_company, date_from, round = False)
        #     if user_currency.is_zero(line_amount):
        #         continue
        #     for partial_line in line.matched_debit_ids:
        #         if partial_line.max_date <= date_from:
        #             line_amount += partial_line.company_id.currency_id._convert(partial_line.amount, user_currency, user_company, date_from, round = False)
        #     for partial_line in line.matched_credit_ids:
        #         if partial_line.max_date <= date_from:
        #             line_amount -= partial_line.company_id.currency_id._convert(partial_line.amount, user_currency, user_company, date_from, round = False)
        #     line_amount = user_currency.round(line_amount)
        #     if not self.env.company.currency_id.is_zero(line_amount):
        #         undue_amounts[partner_id] += line_amount
        #         lines.setdefault(partner_id, [])
        #         lines[partner_id].append({
        #             'line': line,
        #             'amount': line_amount,
        #             'period': 6,
        #         })

        # for partner in partners:
        #     if partner['partner_id'] is None:
        #         partner['partner_id'] = False
        #     at_least_one_amount = False
        #     values = {}
        #     undue_amt = 0.0
        #     if partner['partner_id'] in undue_amounts:  # Making sure this partner actually was found by the query
        #         undue_amt = undue_amounts[partner['partner_id']]

        #     total[6] = total[6] + undue_amt
        #     values['direction'] = undue_amt
        #     if not float_is_zero(values['direction'], precision_rounding=self.env.company.currency_id.rounding):
        #         at_least_one_amount = True

        #     for i in range(5):
        #         during = False
        #         if partner['partner_id'] in history[i]:
        #             during = [history[i][partner['partner_id']]]
        #         # Adding counter
        #         total[(i)] = total[(i)] + (during and during[0] or 0)
        #         values[str(i)] = during and during[0] or 0.0
        #         if not float_is_zero(values[str(i)], precision_rounding=self.env.company.currency_id.rounding):
        #             at_least_one_amount = True
        #     values['total'] = sum([values['direction']] + [values[str(i)] for i in range(5)])
        #     # Add for total
        #     total[(i + 1)] += values['total']
        #     values['partner_id'] = partner['partner_id']
        #     if partner['partner_id']:
        #         name = partner['name'] or ''
        #         values['name'] = len(name) >= 45 and not self.env.context.get('no_format') and name[0:41] + '...' or name
        #         values['trust'] = partner['trust']
        #     else:
        #         values['name'] = _('Unknown Partner')
        #         values['trust'] = False

        #     if at_least_one_amount or (self._context.get('include_nullified_amount') and lines[partner['partner_id']]):
        #         res.append(values)
        # return res, total, lines