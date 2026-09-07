# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from datetime import date, datetime, timedelta
import calendar


class TravelDashboard(models.AbstractModel):
    _name = 'travel.dashboard'
    _description = 'Travel OS Dashboard Service & Work Cockpit'

    @api.model
    def get_dashboard_data(self, role=None):
        """
        Unified service method providing secure, role-filtered dashboard data
        and Daily Execution Cockpit driven by Odoo native mail.activity.
        """
        user = self.env.user
        today = fields.Date.context_today(self)
        first_day_of_month = today.replace(day=1)
        last_day_of_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])

        # Security & Role determination
        is_admin = user.has_group('base.group_system') or user.has_group('alamia_travel_core.group_travel_admin')
        is_ceo = user.has_group('alamia_travel_core.travel_role_ceo') or is_admin
        is_ops_director = user.has_group('alamia_travel_core.travel_role_operations_director') or is_ceo
        is_sales_director = user.has_group('alamia_travel_core.travel_role_sales_director') or is_ceo
        is_ops_marketing = user.has_group('alamia_travel_core.travel_role_operations_marketing') or is_ops_director

        # Determine effective role view
        if not role:
            if is_ceo:
                role = 'ceo'
            elif is_ops_director:
                role = 'operations'
            elif is_sales_director:
                role = 'sales'
            elif is_ops_marketing:
                role = 'ops_marketing'
            else:
                role = 'sales'

        # Verify role authorization
        if role == 'ceo' and not is_ceo:
            raise AccessError(_("You do not have permission to view the CEO Executive Dashboard."))
        elif role == 'operations' and not is_ops_director:
            raise AccessError(_("You do not have permission to view the Operations Dashboard."))
        elif role == 'sales' and not (is_sales_director or is_ops_marketing or is_ceo):
            raise AccessError(_("You do not have permission to view the Sales Dashboard."))
        elif role == 'ops_marketing' and not (is_ops_marketing or is_ceo):
            raise AccessError(_("You do not have permission to view the Operations & Marketing Dashboard."))

        currency = self.env.company.currency_id
        currency_symbol = currency.symbol or 'Rs'

        # -------------------------------------------------------------
        # 1. DAILY WORK COCKPIT — mail.activity Driven
        # -------------------------------------------------------------
        activity_model = self.env['mail.activity']
        my_activities = activity_model.search([('user_id', '=', user.id)])

        def format_activity(act):
            return {
                'id': act.id,
                'res_model': act.res_model,
                'res_id': act.res_id,
                'res_name': act.res_name or _('Record #%s') % act.res_id,
                'activity_type_id': act.activity_type_id.id,
                'activity_type': act.activity_type_id.name,
                'activity_icon': act.activity_type_id.icon or 'fa-tasks',
                'summary': act.summary or act.activity_type_id.name,
                'note': act.note or '',
                'date_deadline': str(act.date_deadline),
                'assigned_by': act.create_uid.name if act.create_uid else _('System'),
                'user_id': act.user_id.id if act.user_id else False,
                'user_name': act.user_id.name if act.user_id else _('Unassigned'),
                'state': 'overdue' if act.date_deadline < today else ('today' if act.date_deadline == today else 'upcoming')
            }

        act_overdue = [format_activity(a) for a in my_activities.filtered(lambda a: a.date_deadline < today).sorted('date_deadline')]
        act_today = [format_activity(a) for a in my_activities.filtered(lambda a: a.date_deadline == today)]
        act_upcoming = [format_activity(a) for a in my_activities.filtered(lambda a: a.date_deadline > today).sorted('date_deadline')[:20]]

        # Unassigned Activities (For Managers & Staff)
        unassigned_acts = [format_activity(a) for a in activity_model.search([('user_id', '=', False)], limit=20)]

        # Available Activity Types for scheduling follow-ups
        activity_types = [{'id': t.id, 'name': t.name} for t in self.env['mail.activity.type'].search([])]

        # -------------------------------------------------------------
        # 2. MANAGER TEAM WORKLOAD MATRIX (Dynamic resolution from groups)
        # -------------------------------------------------------------
        team_workload = []
        team_users = self.env['res.users'].search([
            ('share', '=', False),
            ('active', '=', True)
        ], order='name')

        for u in team_users:
            u_acts = activity_model.search([('user_id', '=', u.id)])
            u_overdue = len(u_acts.filtered(lambda a: a.date_deadline < today))
            u_today = len(u_acts.filtered(lambda a: a.date_deadline == today))
            u_upcoming = len(u_acts.filtered(lambda a: a.date_deadline > today))
            u_total = len(u_acts)

            if u_overdue > 3 or u_today > 8:
                status = 'overloaded'
                status_label = 'Overloaded'
            elif u_overdue > 0:
                status = 'attention'
                status_label = 'Attention'
            else:
                status = 'ok'
                status_label = 'OK'

            team_workload.append({
                'user_id': u.id,
                'user_name': u.name,
                'overdue_count': u_overdue,
                'today_count': u_today,
                'upcoming_count': u_upcoming,
                'total_open': u_total,
                'status': status,
                'status_label': status_label,
            })

        # -------------------------------------------------------------
        # 3. DATA-DRIVEN ATTENTION ITEMS & EXCEPTIONS
        # -------------------------------------------------------------
        three_days_ago = today - timedelta(days=3)
        seven_days_ago = today - timedelta(days=7)

        # Unconfirmed sales older than 3 days
        old_draft_sales = self.env['travel.sale'].search_count([
            ('state', '=', 'draft'),
            ('date_sale', '<=', three_days_ago)
        ])

        # Overdue customer receivables older than 7 days
        overdue_receivables_7d_moves = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('invoice_date_due', '<=', seven_days_ago)
        ])
        overdue_receivables_7d_total = sum(overdue_receivables_7d_moves.mapped('amount_residual'))
        overdue_receivables_7d_count = len(overdue_receivables_7d_moves)

        # Pending draft expenses
        pending_expenses_count = self.env['travel.expense'].search_count([('state', '=', 'draft')])

        # Unpaid vendor bills
        unpaid_bills_moves = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ['not_paid', 'partial'])
        ])
        unpaid_bills_total = sum(unpaid_bills_moves.mapped('amount_residual'))

        attention_items = {
            'unassigned_activities_count': len(unassigned_acts),
            'old_draft_sales_count': old_draft_sales,
            'overdue_receivables_7d_count': overdue_receivables_7d_count,
            'overdue_receivables_7d_total': overdue_receivables_7d_total,
            'pending_expenses_count': pending_expenses_count,
            'unpaid_bills_total': unpaid_bills_total,
        }

        # -------------------------------------------------------------
        # 4. CORE SALES & FINANCIAL AGGREGATIONS
        # -------------------------------------------------------------
        all_sales = self.env['travel.sale'].search([])
        today_sales = all_sales.filtered(lambda s: s.date_sale == today and s.state != 'cancelled')
        month_sales = all_sales.filtered(lambda s: s.date_sale and s.date_sale >= first_day_of_month and s.date_sale <= last_day_of_month and s.state != 'cancelled')
        my_today_sales = today_sales.filtered(lambda s: s.salesperson_id.id == user.id)
        my_month_sales = month_sales.filtered(lambda s: s.salesperson_id.id == user.id)

        # Collections (Inbound Payments)
        payment_model = self.env['account.payment']
        today_payments = payment_model.search([
            ('payment_type', '=', 'inbound'),
            ('state', '=', 'posted'),
            ('date', '=', today)
        ])
        month_payments = payment_model.search([
            ('payment_type', '=', 'inbound'),
            ('state', '=', 'posted'),
            ('date', '>=', first_day_of_month),
            ('date', '<=', last_day_of_month)
        ])
        today_collections_total = sum(today_payments.mapped('amount'))
        month_collections_total = sum(month_payments.mapped('amount'))

        # Receivables & Payables
        posted_out_invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted')
        ])
        total_receivables = sum(posted_out_invoices.mapped('amount_residual'))

        posted_in_invoices = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted')
        ])
        total_payables = sum(posted_in_invoices.mapped('amount_residual'))

        # Cash & Bank Positions
        cash_journals = self.env['account.journal'].search([('type', '=', 'cash')])
        bank_journals = self.env['account.journal'].search([('type', '=', 'bank')])
        
        cash_position = 0.0
        for j in cash_journals:
            if hasattr(j, 'current_statement_balance'):
                cash_position += j.current_statement_balance
            elif j.default_account_id:
                lines = self.env['account.move.line'].search([('account_id', '=', j.default_account_id.id), ('parent_state', '=', 'posted')])
                cash_position += sum(lines.mapped('balance'))

        bank_position = 0.0
        for j in bank_journals:
            if hasattr(j, 'current_statement_balance'):
                bank_position += j.current_statement_balance
            elif j.default_account_id:
                lines = self.env['account.move.line'].search([('account_id', '=', j.default_account_id.id), ('parent_state', '=', 'posted')])
                bank_position += sum(lines.mapped('balance'))

        # Sales by Service Breakdown
        service_sales_map = {}
        for sale in month_sales:
            for line in sale.line_ids:
                service_name = line.service_id.name or 'Other'
                if service_name not in service_sales_map:
                    service_sales_map[service_name] = {'name': service_name, 'count': 0, 'selling': 0.0, 'cost': 0.0, 'profit': 0.0}
                service_sales_map[service_name]['count'] += 1
                service_sales_map[service_name]['selling'] += line.selling_amount
                service_sales_map[service_name]['cost'] += line.cost_amount
                service_sales_map[service_name]['profit'] += line.gross_profit
        sales_by_service = sorted(service_sales_map.values(), key=lambda x: x['selling'], reverse=True)

        # Sales by Staff Breakdown
        staff_sales_map = {}
        for sale in month_sales:
            staff_name = sale.salesperson_id.name or 'Unassigned'
            if staff_name not in staff_sales_map:
                staff_sales_map[staff_name] = {'name': staff_name, 'count': 0, 'selling': 0.0, 'profit': 0.0}
            staff_sales_map[staff_name]['count'] += 1
            staff_sales_map[staff_name]['selling'] += sale.total_selling_amount
            staff_sales_map[staff_name]['profit'] += sale.gross_profit
        sales_by_staff = sorted(staff_sales_map.values(), key=lambda x: x['selling'], reverse=True)

        # Top Debtors & Creditors
        customer_residual_map = {}
        for inv in posted_out_invoices.filtered(lambda i: i.amount_residual > 0):
            cust_name = inv.partner_id.name or 'Unknown Customer'
            cust_id = inv.partner_id.id
            if cust_id not in customer_residual_map:
                customer_residual_map[cust_id] = {'id': cust_id, 'name': cust_name, 'outstanding': 0.0}
            customer_residual_map[cust_id]['outstanding'] += inv.amount_residual
        outstanding_customers = sorted(customer_residual_map.values(), key=lambda x: x['outstanding'], reverse=True)[:10]

        # Recent Transactions
        recent_sales_records = all_sales.sorted(key=lambda s: s.id, reverse=True)[:10]
        recent_sales = [{
            'id': s.id,
            'name': s.name,
            'customer': s.customer_id.name,
            'date': str(s.date_sale),
            'salesperson': s.salesperson_id.name,
            'amount': s.total_selling_amount,
            'profit': s.gross_profit,
            'state': s.state,
            'payment_status': getattr(s, 'payment_status', 'unpaid')
        } for s in recent_sales_records]

        workload = {
            'draft': len(all_sales.filtered(lambda s: s.state == 'draft')),
            'confirmed': len(all_sales.filtered(lambda s: s.state == 'confirmed')),
            'in_progress': len(all_sales.filtered(lambda s: s.state == 'in_progress')),
            'completed': len(all_sales.filtered(lambda s: s.state == 'completed')),
            'cancelled': len(all_sales.filtered(lambda s: s.state == 'cancelled')),
        }
        pending_transactions_count = workload['draft'] + workload['confirmed'] + workload['in_progress']

        # Construct Final Role Payload
        data = {
            'role': role,
            'user_name': user.name,
            'currency_symbol': currency_symbol,
            'my_activities': {
                'overdue': act_overdue,
                'today': act_today,
                'upcoming': act_upcoming,
                'overdue_count': len(act_overdue),
                'today_count': len(act_today),
                'upcoming_count': len(act_upcoming),
            },
            'unassigned_activities': unassigned_acts,
            'activity_types': activity_types,
            'team_workload': team_workload,
            'attention_items': attention_items,
            'kpis': {
                'today_sales': sum(today_sales.mapped('total_selling_amount')),
                'today_sales_count': len(today_sales),
                'today_collections': today_collections_total,
                'monthly_sales': sum(month_sales.mapped('total_selling_amount')),
                'monthly_sales_count': len(month_sales),
                'monthly_gross_profit': sum(month_sales.mapped('gross_profit')),
                'total_receivables': total_receivables,
                'total_payables': total_payables,
                'cash_position': cash_position,
                'bank_position': bank_position,
                'my_today_sales': sum(my_today_sales.mapped('total_selling_amount')),
                'my_month_sales': sum(my_month_sales.mapped('total_selling_amount')),
                'pending_transactions_count': pending_transactions_count,
            },
            'sales_by_service': sales_by_service,
            'sales_by_staff': sales_by_staff,
            'outstanding_customers': outstanding_customers,
            'recent_sales': recent_sales,
            'workload': workload,
        }

        return data

    @api.model
    def action_complete_activity(self, activity_id, outcome, feedback=None, next_activity=None):
        """
        Completes an activity capturing outcome and feedback note,
        and optionally schedules the next activity immediately.
        """
        activity = self.env['mail.activity'].sudo().browse(activity_id)
        if not activity.exists():
            raise UserError(_("Activity not found or already completed."))

        outcome_note = _("Outcome: %s\nFeedback: %s") % (outcome, feedback or 'N/A')
        res_model = activity.res_model
        res_id = activity.res_id

        # Mark activity complete via native Odoo feedback mechanism
        activity.action_feedback(feedback=outcome_note)

        # Schedule next follow-up activity if requested
        if next_activity and next_activity.get('activity_type_id') and next_activity.get('date_deadline'):
            self.env['mail.activity'].sudo().create({
                'res_model_id': self.env['ir.model']._get_id(res_model),
                'res_id': res_id,
                'activity_type_id': int(next_activity['activity_type_id']),
                'summary': next_activity.get('summary') or _('Follow-up Activity'),
                'note': next_activity.get('note') or '',
                'date_deadline': next_activity['date_deadline'],
                'user_id': int(next_activity.get('user_id') or self.env.user.id),
            })

        return True

    @api.model
    def action_reschedule_activity(self, activity_id, new_date):
        """ Reschedules an activity deadline date """
        activity = self.env['mail.activity'].sudo().browse(activity_id)
        if not activity.exists():
            raise UserError(_("Activity not found."))
        activity.write({'date_deadline': new_date})
        return True

    @api.model
    def action_reassign_activity(self, activity_id, new_user_id, new_date=None):
        """ Reassigns an activity to a new user for manager workload balancing """
        activity = self.env['mail.activity'].sudo().browse(activity_id)
        if not activity.exists():
            raise UserError(_("Activity not found."))
        vals = {'user_id': int(new_user_id)}
        if new_date:
            vals['date_deadline'] = new_date
        activity.write(vals)
        return True
