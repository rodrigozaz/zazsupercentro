# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import copy
import ast

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import formatLang
from odoo.tools import float_is_zero, ustr
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.addons.account_reports.models.account_financial_report import IrModuleModule
import logging

_logger = logging.getLogger(__name__)

class AccountFinancialReport(models.Model):
    _inherit = "account.financial.html.report"

    def _get_columns_name(self, options):
        rslt = super(AccountFinancialReport, self)._get_columns_name(options)
        for account in self.env['account.analytic.account'].browse(options.get('analytic_accounts')):
            rslt.append({'name': account.name, 'class': 'number'})
        return rslt
    
    def _get_lines(self, options, line_id=None):
        line_obj = self.line_ids
        if line_id:
            line_obj = self.env['account.financial.html.report.line'].search([('id', '=', line_id)])
        if options.get('comparison') and options.get('comparison').get('periods'):
            line_obj = line_obj.with_context(periods=options['comparison']['periods'])
        if options.get('ir_filters'):
            line_obj = line_obj.with_context(periods=options.get('ir_filters'))

        currency_table = self._get_currency_table()
        domain, group_by = self._get_filter_info(options)

        if group_by:
            options['groups'] = {}
            options['groups']['fields'] = group_by
            options['groups']['ids'] = self._get_groups(domain, group_by)

        amount_of_periods = len((options.get('comparison') or {}).get('periods') or []) + 1
        amount_of_group_ids = len(options.get('groups', {}).get('ids') or []) or 1
        linesDicts = [[{} for _ in range(0, amount_of_group_ids)] for _ in range(0, amount_of_periods)]
        res = line_obj.with_context(
            filter_domain=domain,
        )._get_lines(self, currency_table, options, linesDicts)
        return res

class AccountFinancialReportLine(models.Model):
    _inherit = "account.financial.html.report.line"
    
    def _get_lines(self, financial_report, currency_table, options, linesDicts):
        accounts = options.get('analytic_accounts')
        self.env['ir.config_parameter'].sudo().set_param('afrl.accounts', options.get('analytic_accounts'))
        self.env['ir.config_parameter'].sudo().set_param('afrl.account', None)
        final_result_table = []
        comparison_table = [options.get('date')]
        comparison_table += options.get('comparison') and options['comparison'].get('periods', []) or []
        currency_precision = self.env.company.currency_id.rounding
        # build comparison table
        for line in self:
            res = []
            debit_credit = len(comparison_table) == 1
            domain_ids = {'line'}
            k = 0

            for period in comparison_table:
                date_from = period.get('date_from', False)
                date_to = period.get('date_to', False) or period.get('date', False)
                date_from, date_to, strict_range = line.with_context(date_from=date_from, date_to=date_to)._compute_date_range()
                account_names = options.get('selected_analytic_account_names')
                accounts = self.env['account.analytic.account'].search([('name', 'in', account_names)]).ids
                r = line.with_context(date_from=date_from,
                                      date_to=date_to,
                                      strict_range=strict_range)._eval_formula(financial_report,
                                                                               debit_credit,
                                                                               currency_table,
                                                                               linesDicts[k],
                                                                               accounts,
                                                                               groups=options.get('groups'))
                debit_credit = False
                res.extend(r)
                for column in r:
                    domain_ids.update(column)
                k += 1
            
            res = line._put_columns_together(res, domain_ids)

            if line.hide_if_zero and all([float_is_zero(k, precision_rounding=currency_precision) for k in res['line']]):
                continue

            # Post-processing ; creating line dictionnary, building comparison, computing total for extended, formatting
            vals = {
                'id': line.id,
                'name': line.name,
                'level': line.level,
                'class': 'o_account_reports_totals_below_sections' if self.env.company.totals_below_sections else '',
                'columns': [{'name': l} for l in res['line']],
                'unfoldable': len(domain_ids) > 1 and line.show_domain != 'always',
                'unfolded': line.id in options.get('unfolded_lines', []) or line.show_domain == 'always',
                'page_break': line.print_on_new_page,
            }

            if financial_report.tax_report and line.domain and not line.action_id:
                vals['caret_options'] = 'tax.report.line'

            if line.action_id:
                vals['action_id'] = line.action_id.id
            domain_ids.remove('line')
            lines = [vals]
            groupby = line.groupby or 'aml'
            if line.id in options.get('unfolded_lines', []) or line.show_domain == 'always':
                if line.groupby:
                    domain_ids = sorted(list(domain_ids), key=lambda k: line._get_gb_name(k))
                for domain_id in domain_ids:
                    name = line._get_gb_name(domain_id)
                    if not self.env.context.get('print_mode') or not self.env.context.get('no_format'):
                        name = name[:40] + '...' if name and len(name) >= 45 else name
                    vals = {
                        'id': 'financial_report_group_%s_%s' % (line.id, domain_id),
                        'name': name,
                        'level': line.level,
                        'parent_id': line.id,
                        'columns': [{'name': l} for l in res[domain_id]],
                        'caret_options': groupby == 'account_id' and 'account.account' or groupby,
                        'financial_group_line_id': line.id,
                    }
                    if line.financial_report_id.name == 'Aged Receivable':
                        vals['trust'] = self.env['res.partner'].browse([domain_id]).trust
                    lines.append(vals)
                if domain_ids and self.env.company.totals_below_sections:
                    lines.append({
                        'id': 'total_' + str(line.id),
                        'name': _('Total') + ' ' + line.name,
                        'level': line.level,
                        'class': 'o_account_reports_domain_total',
                        'parent_id': line.id,
                        'columns': copy.deepcopy(lines[0]['columns']),
                    })

            for vals in lines:
                if len(comparison_table) == 2 and not options.get('groups'):
                    vals['columns'].append(line._build_cmp(vals['columns'][0]['name'], vals['columns'][1]['name']))
                    for i in [0, 1]:
                        vals['columns'][i] = line._format(vals['columns'][i])
                else:
                    vals['columns'] = [line._format(v) for v in vals['columns']]
                if not line.formulas:
                    vals['columns'] = [{'name': ''} for k in vals['columns']]

            if len(lines) == 1:
                new_lines = line.children_ids._get_lines(financial_report, currency_table, options, linesDicts)
                if new_lines and line.formulas:
                    if self.env.company.totals_below_sections:
                        divided_lines = self._divide_line(lines[0])
                        result = [divided_lines[0]] + new_lines + [divided_lines[-1]]
                    else:
                        result = [lines[0]] + new_lines
                else:
                    if not new_lines and not lines[0]['unfoldable'] and line.hide_if_empty:
                        lines = []
                    result = lines + new_lines
            else:
                result = lines
            final_result_table += result
        return final_result_table
    
    def _get_sum(self, currency_table, financial_report, field_names=None, account=None):
        ''' Returns the sum of the amls in the domain '''
        if not field_names:
            field_names = ['debit', 'credit', 'balance', 'amount_residual']
        res = dict((fn, 0.0) for fn in field_names)
        if self.domain:
            date_from, date_to, strict_range = \
                self._compute_date_range()
            res = self.with_context(strict_range=strict_range, date_from=date_from, date_to=date_to, active_test=False)._compute_line(currency_table, financial_report, group_by=self.groupby, domain=self._get_aml_domain(), account=account)
        return res

    def _get_balance(self, linesDict, currency_table, financial_report, field_names=None, account=None):
        results = []
        if not field_names:
            field_names = ['debit', 'credit', 'balance']

        for rec in self:
            res = dict((fn, 0.0) for fn in field_names)
            c = FormulaContext(self.env['account.financial.html.report.line'],
                    linesDict, currency_table, financial_report, rec, account=account)
            if rec.formulas:
                for f in rec.formulas.split(';'):
                    [field, formula] = f.split('=')
                    field = field.strip()
                    if field in field_names:
                        try:
                            res[field] = safe_eval(formula, c, nocopy=True)
                        except ValueError as err:
                            if 'division by zero' in err.args[0]:
                                res[field] = 0
                            else:
                                raise err
            results.append(res)
        return results
    
    def _get_column_line(self, financial_report, currency_table, options, linesDicts):
        comparison_table = [options.get('date')]
        comparison_table += options.get('comparison') and options['comparison'].get('periods', []) or []

        # build comparison table
        for line in self:
            res = []
            debit_credit = len(comparison_table) == 1
            domain_ids = {'line'}
            k = 0

            for period in comparison_table:
                date_from = period.get('date_from', False)
                date_to = period.get('date_to', False) or period.get('date', False)
                date_from, date_to, strict_range = line.with_context(date_from=date_from, date_to=date_to)._compute_date_range()

                r = line.with_context(date_from=date_from,
                                      date_to=date_to,
                                      strict_range=strict_range)._eval_formula(financial_report,
                                                                               debit_credit,
                                                                               currency_table,
                                                                               linesDicts[k],
                                                                               groups=options.get('groups'))
                debit_credit = False
                res.extend(r)
                for column in r:
                    domain_ids.update(column)
                k += 1
            
            res = line._put_columns_together(res, domain_ids)
            return res
    
    def _compute_line(self, currency_table, financial_report, group_by=None, domain=[], account=None):
        """ Computes the sum that appeas on report lines when they aren't unfolded. It is using _query_get() function
            of account.move.line which is based on the context, and an additional domain (the field domain on the report
            line) to build the query that will be used.

            @param currency_table: dictionary containing the foreign currencies (key) and their factor (value)
                compared to the current user's company currency
            @param financial_report: browse_record of the financial report we are willing to compute the lines for
            @param group_by: used in case of conditionnal sums on the report line
            @param domain: domain on the report line to consider in the query_get() call

            @returns : a dictionnary that has for each aml in the domain a dictionnary of the values of the fields
        """
        domain = domain and ast.literal_eval(ustr(domain))
        for index, condition in enumerate(domain):
            if condition[0].startswith('tax_ids.'):
                new_condition = (condition[0].partition('.')[2], condition[1], condition[2])
                taxes = self.env['account.tax'].with_context(active_test=False).search([new_condition])
                domain[index] = ('tax_ids', 'in', taxes.ids)
        aml_obj = self.env['account.move.line']
        tables, where_clause, where_params = aml_obj._query_get(domain=self._get_aml_domain())
        if financial_report.tax_report:
            where_clause += ''' AND "account_move_line".tax_exigible = 't' '''
        if account != None and account != True and account != False:
            where_clause += ''' AND "account_move_line".analytic_account_id = {} '''.format(account)
        line = self
        financial_report = self._get_financial_report()

        select, select_params = self._query_get_select_sum(currency_table)
        where_params = select_params + where_params

        if (self.env.context.get('sum_if_pos') or self.env.context.get('sum_if_neg')) and group_by:
            sql = "SELECT account_move_line." + group_by + " as " + group_by + "," + select + " FROM " + tables + " WHERE " + where_clause + " GROUP BY account_move_line." + group_by
            self.env.cr.execute(sql, where_params)
            res = {'balance': 0, 'debit': 0, 'credit': 0, 'amount_residual': 0}
            for row in self.env.cr.dictfetchall():
                if (row['balance'] > 0 and self.env.context.get('sum_if_pos')) or (row['balance'] < 0 and self.env.context.get('sum_if_neg')):
                    for field in ['debit', 'credit', 'balance', 'amount_residual']:
                        res[field] += row[field]
            res['currency_id'] = self.env.company.currency_id.id
            return res

        sql, params = self._build_query_compute_line(select, tables, where_clause, where_params)
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()[0]
        results['currency_id'] = self.env.company.currency_id.id
        return results
        
# Changed FormulaLine Parameters

    def _eval_formula(self, financial_report, debit_credit, currency_table, linesDict_per_group, accounts=None, groups=False):
        account = None
        other_columns = []
        if accounts:
            account = int(accounts.pop(0))
            other_columns += self._eval_formula(financial_report, debit_credit, currency_table, linesDict_per_group, accounts, groups)
#         account = self.env['ir.config_parameter'].sudo().get_param('afrl.account')
        groups = groups or {'fields': [], 'ids': [()]}
        debit_credit = debit_credit and financial_report.debit_credit
        formulas = self._split_formulas()
        currency = self.env.company.currency_id

        line_res_per_group = []

        if not groups['ids']:
            return [{'line': {'balance': 0.0}}] + other_columns

        # this computes the results of the line itself
        for group_index, group in enumerate(groups['ids']):
            self_for_group = self.with_context(group_domain=self._get_group_domain(group, groups))
            linesDict = linesDict_per_group[group_index]
            line = False
            if account != None and account != False:
                line = FormulaLine(self_for_group, currency_table, financial_report, linesDict=linesDict, account=account)
            elif self.code and self.code in linesDict:
                line = linesDict[self.code]
            elif formulas and formulas['balance'].strip() == 'count_rows' and self.groupby:
                line_res_per_group.append({'line': {'balance': self_for_group._get_rows_count()}})
            elif formulas and formulas['balance'].strip() == 'from_context':
                line_res_per_group.append({'line': {'balance': self_for_group._get_value_from_context()}})
            else:
                line = FormulaLine(self_for_group, currency_table, financial_report, linesDict=linesDict, account=account)

            if line:
                res = {}
                res['balance'] = line.balance
                res['balance'] = currency.round(line.balance) if self.figure_type != 'percents' else line.balance
                if debit_credit:
                    res['credit'] = currency.round(line.credit)
                    res['debit'] = currency.round(line.debit)
                line_res_per_group.append(res)

        # don't need any groupby lines for count_rows and from_context formulas
        if all('line' in val for val in line_res_per_group):
            return other_columns + line_res_per_group

        columns = []
        # this computes children lines in case the groupby field is set
        if self.domain and self.groupby and self.show_domain != 'never':
            if self.groupby not in self.env['account.move.line']:
                raise ValueError(_('Groupby should be a field from account.move.line'))

            groupby = [self.groupby or 'id']
            if groups:
                groupby = groups['fields'] + groupby
            groupby = ', '.join(['"account_move_line".%s' % field for field in groupby])

            aml_obj = self.env['account.move.line']
            tables, where_clause, where_params = aml_obj._query_get(domain=self._get_aml_domain())
            if financial_report.tax_report:
                where_clause += ''' AND "account_move_line".tax_exigible = 't' '''
            
            if account != False and account != None:
                where_clause += ''' AND "account_move_line".analytic_account_id = {} '''.format(account)
            select, params = self._query_get_select_sum(currency_table)
            params += where_params

            sql, params = self._build_query_eval_formula(groupby, select, tables, where_clause, params)
            self.env.cr.execute(sql, params)
            results = self.env.cr.fetchall()
            for group_index, group in enumerate(groups['ids']):
                linesDict = linesDict_per_group[group_index]
                results_for_group = [result for result in results if group == result[:len(group)]]
                if results_for_group:
                    results_for_group = [r[len(group):] for r in results_for_group]
                    results_for_group = dict([(k[0], {'balance': k[1], 'amount_residual': k[2], 'debit': k[3], 'credit': k[4]}) for k in results_for_group])
                    c = FormulaContext(self.env['account.financial.html.report.line'].with_context(group_domain=self._get_group_domain(group, groups)),
                                       linesDict, currency_table, financial_report, only_sum=True)
                    if formulas:
                        for key in results_for_group:
                            c['sum'] = FormulaLine(results_for_group[key], currency_table, financial_report, type='not_computed', account=account)
                            c['sum_if_pos'] = FormulaLine(results_for_group[key]['balance'] >= 0.0 and results_for_group[key] or {'balance': 0.0},
                                                          currency_table, financial_report, type='not_computed', account=account)
                            c['sum_if_neg'] = FormulaLine(results_for_group[key]['balance'] <= 0.0 and results_for_group[key] or {'balance': 0.0},
                                                          currency_table, financial_report, type='not_computed', account=account)
                            for col, formula in formulas.items():
                                if col in results_for_group[key]:
                                    results_for_group[key][col] = safe_eval(formula, c, nocopy=True)
                    to_del = []
                    for key in results_for_group:
                        if self.env.company.currency_id.is_zero(results_for_group[key]['balance']):
                            to_del.append(key)
                    for key in to_del:
                        del results_for_group[key]
                    results_for_group.update({'line': line_res_per_group[group_index]})
                    columns.append(results_for_group)
                else:
                    res_vals = {'balance': 0.0}
                    if debit_credit:
                        res_vals.update({'debit': 0.0, 'credit': 0.0})
                    columns.append({'line': res_vals})
        if columns:
            return other_columns + columns
        return other_columns + [{'line': res} for res in line_res_per_group]
    
class FormulaLine(object):
    def __init__(self, obj, currency_table, financial_report, type='balance', linesDict=None, account=None):
        if linesDict is None:
            linesDict = {}
        fields = dict((fn, 0.0) for fn in ['debit', 'credit', 'balance'])
#         if account != None:
        if type == 'balance':
            fields = obj._get_balance(linesDict, currency_table, financial_report, account=account)[0]
            linesDict[obj.code] = self
        elif type in ['sum', 'sum_if_pos', 'sum_if_neg']:
            if type == 'sum_if_neg':
                obj = obj.with_context(sum_if_neg=True)
            if type == 'sum_if_pos':
                obj = obj.with_context(sum_if_pos=True)
            if obj._name == 'account.financial.html.report.line':
                fields = obj._get_sum(currency_table, financial_report, account=account)
                self.amount_residual = fields['amount_residual']
            elif obj._name == 'account.move.line':
                self.amount_residual = 0.0
                field_names = ['debit', 'credit', 'balance', 'amount_residual']
                res = obj.env['account.financial.html.report.line']._compute_line(currency_table, financial_report, account=account)
                for field in field_names:
                    fields[field] = res[field]
                self.amount_residual = fields['amount_residual']
        elif type == 'not_computed':
            for field in fields:
                fields[field] = obj.get(field, 0)
            self.amount_residual = obj.get('amount_residual', 0)
        elif type == 'null':
            self.amount_residual = 0.0
        self.balance = fields['balance']
        self.credit = fields['credit']
        self.debit = fields['debit']
        
class FormulaContext(dict):
    def __init__(self, reportLineObj, linesDict, currency_table, financial_report, curObj=None, only_sum=False, account=None, *data):
        self.reportLineObj = reportLineObj
        self.curObj = curObj
        self.linesDict = linesDict
        self.currency_table = currency_table
        self.only_sum = only_sum
        self.financial_report = financial_report
        self.account = account
        return super(FormulaContext, self).__init__(data)

    def __getitem__(self, item):
        formula_items = ['sum', 'sum_if_pos', 'sum_if_neg']
        if item in set(__builtins__.keys()) - set(formula_items):
            return super(FormulaContext, self).__getitem__(item)

        if self.only_sum and item not in formula_items:
            return FormulaLine(self.curObj, self.currency_table, self.financial_report, type='null', account=self.account)
        if self.get(item):
            return super(FormulaContext, self).__getitem__(item)
        if self.linesDict.get(item):
            return self.linesDict[item]
        if item == 'sum':
            res = FormulaLine(self.curObj, self.currency_table, self.financial_report, type='sum', account=self.account)
            self['sum'] = res
            return res
        if item == 'sum_if_pos':
            res = FormulaLine(self.curObj, self.currency_table, self.financial_report, type='sum_if_pos', account=self.account)
            self['sum_if_pos'] = res
            return res
        if item == 'sum_if_neg':
            res = FormulaLine(self.curObj, self.currency_table, self.financial_report, type='sum_if_neg', account=self.account)
            self['sum_if_neg'] = res
            return res
        if item == 'NDays':
            d1 = fields.Date.from_string(self.curObj.env.context['date_from'])
            d2 = fields.Date.from_string(self.curObj.env.context['date_to'])
            res = (d2 - d1).days
            self['NDays'] = res
            return res
        if item == 'count_rows':
            return self.curObj._get_rows_count()
        if item == 'from_context':
            return self.curObj._get_value_from_context()
        line_id = self.reportLineObj.search([('code', '=', item)], limit=1)
        if line_id:
            date_from, date_to, strict_range = line_id._compute_date_range()
            res = FormulaLine(line_id.with_context(strict_range=strict_range, date_from=date_from, date_to=date_to), self.currency_table, self.financial_report, linesDict=self.linesDict, account=self.account)
            self.linesDict[item] = res
            return res
        return super(FormulaContext, self).__getitem__(item)