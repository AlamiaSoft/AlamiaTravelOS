from odoo import api, fields, models, _
from odoo.exceptions import AccessError
from datetime import date, datetime, timedelta
import calendar

class TravelDashboard(models.AbstractModel):
    _name = 'travel.dashboard'
    _description = 'Travel OS Dashboard Service'

    @api.model
    def get_dashboard_data(self, role=None):
        """
        Unified service method providing secure, role-filtered dashboard data
        for CEO, Operations Director, Sales Director, and Assistant Ops & Marketing.
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
        # CORE SALES AGGREGATIONS
        # -------------------------------------------------------------
        all_sales = self.env['travel.sale'].search([])
        today_sales = all_sales.filtered(lambda s: s.date_sale == today and s.state != 'cancelled')
        month_sales = all_sales.filtered(lambda s: s.date_sale and s.date_sale >= first_day_of_month and s.date_sale <= last_day_of_month and s.state != 'cancelled')
        my_today_sales = today_sales.filtered(lambda s: s.salesperson_id.id == user.id)
        my_month_sales = month_sales.filtered(lambda s: s.salesperson_id.id == user.id)

        # -------------------------------------------------------------
        # COLLECTIONS & PAYMENTS (Inbound Customer Collections)
        # -------------------------------------------------------------
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

        # -------------------------------------------------------------
        # RECEIVABLES & PAYABLES (Odoo Native account.move)
        # -------------------------------------------------------------
        # Out Invoices (Customer Invoices)
        posted_out_invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted')
        ])
        total_receivables = sum(posted_out_invoices.mapped('amount_residual'))

        # In Invoices (Vendor Bills)
        posted_in_invoices = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted')
        ])
        total_payables = sum(posted_in_invoices.mapped('amount_residual'))

        # -------------------------------------------------------------
        # CASH & BANK POSITIONS
        # -------------------------------------------------------------
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

        # -------------------------------------------------------------
        # SALES BY SERVICE BREAKDOWN
        # -------------------------------------------------------------
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

        # -------------------------------------------------------------
        # SALES BY STAFF / SALESPERSON PERFORMANCE
        # -------------------------------------------------------------
        staff_sales_map = {}
        for sale in month_sales:
            staff_name = sale.salesperson_id.name or 'Unassigned'
            if staff_name not in staff_sales_map:
                staff_sales_map[staff_name] = {'name': staff_name, 'count': 0, 'selling': 0.0, 'profit': 0.0}
            staff_sales_map[staff_name]['count'] += 1
            staff_sales_map[staff_name]['selling'] += sale.total_selling_amount
            staff_sales_map[staff_name]['profit'] += sale.gross_profit
        
        sales_by_staff = sorted(staff_sales_map.values(), key=lambda x: x['selling'], reverse=True)

        # -------------------------------------------------------------
        # OUTSTANDING CUSTOMER BALANCES (Top Debtors)
        # -------------------------------------------------------------
        customer_residual_map = {}
        for inv in posted_out_invoices.filtered(lambda i: i.amount_residual > 0):
            cust_name = inv.partner_id.name or 'Unknown Customer'
            cust_id = inv.partner_id.id
            if cust_id not in customer_residual_map:
                customer_residual_map[cust_id] = {'id': cust_id, 'name': cust_name, 'outstanding': 0.0}
            customer_residual_map[cust_id]['outstanding'] += inv.amount_residual
        
        outstanding_customers = sorted(customer_residual_map.values(), key=lambda x: x['outstanding'], reverse=True)[:10]

        # -------------------------------------------------------------
        # SUPPLIER PAYABLES (Top Creditors)
        # -------------------------------------------------------------
        supplier_residual_map = {}
        for bill in posted_in_invoices.filtered(lambda b: b.amount_residual > 0):
            supp_name = bill.partner_id.name or 'Unknown Supplier'
            supp_id = bill.partner_id.id
            if supp_id not in supplier_residual_map:
                supplier_residual_map[supp_id] = {'id': supp_id, 'name': supp_name, 'payable': 0.0}
            supplier_residual_map[supp_id]['payable'] += bill.amount_residual
        
        supplier_payables = sorted(supplier_residual_map.values(), key=lambda x: x['payable'], reverse=True)[:10]

        # -------------------------------------------------------------
        # TOP CUSTOMERS (By Sales Volume)
        # -------------------------------------------------------------
        customer_sales_map = {}
        for sale in month_sales:
            c_name = sale.customer_id.name or 'Unknown'
            c_id = sale.customer_id.id
            if c_id not in customer_sales_map:
                customer_sales_map[c_id] = {'id': c_id, 'name': c_name, 'total_sales': 0.0, 'count': 0}
            customer_sales_map[c_id]['total_sales'] += sale.total_selling_amount
            customer_sales_map[c_id]['count'] += 1
        
        top_customers = sorted(customer_sales_map.values(), key=lambda x: x['total_sales'], reverse=True)[:10]

        # -------------------------------------------------------------
        # RECENT TRANSACTIONS / RECENT SALES
        # -------------------------------------------------------------
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

        # -------------------------------------------------------------
        # OPERATIONAL WORKLOAD / STATUS BREAKDOWN
        # -------------------------------------------------------------
        workload = {
            'draft': len(all_sales.filtered(lambda s: s.state == 'draft')),
            'confirmed': len(all_sales.filtered(lambda s: s.state == 'confirmed')),
            'in_progress': len(all_sales.filtered(lambda s: s.state == 'in_progress')),
            'completed': len(all_sales.filtered(lambda s: s.state == 'completed')),
            'cancelled': len(all_sales.filtered(lambda s: s.state == 'cancelled')),
        }
        pending_transactions_count = workload['draft'] + workload['confirmed'] + workload['in_progress']

        # Build Response Structure
        data = {
            'role': role,
            'user_name': user.name,
            'currency_symbol': currency_symbol,
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
            'supplier_payables': supplier_payables,
            'top_customers': top_customers,
            'recent_sales': recent_sales,
            'workload': workload,
        }

        return data
