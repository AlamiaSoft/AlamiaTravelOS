# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError


class TestPhase2Features(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Partner = self.env['res.partner']
        self.TravelSale = self.env['travel.sale']
        self.TravelSaleLine = self.env['travel.sale.line']
        self.ServiceCatalog = self.env['travel.service.catalog']
        self.ServicePackage = self.env['travel.service.package']
        self.ExpenseCategory = self.env['travel.expense.category']
        self.TravelExpense = self.env['travel.expense']

        # Setup customer & supplier & subagent
        self.customer = self.Partner.create({
            'name': 'Test Customer Phase2',
            'is_travel_customer': True,
        })
        self.supplier = self.Partner.create({
            'name': 'Test Supplier Phase2',
            'is_travel_supplier': True,
        })
        self.agent = self.Partner.create({
            'name': 'Test SubAgent Phase2',
            'is_travel_agent': True,
            'agent_code': 'AGT-001',
            'default_commission_rate': 10.0,
        })

        # Setup services
        self.service_visa = self.ServiceCatalog.create({
            'name': 'Saudi Visit Visa Test',
            'code': 'VISA-SA-TEST',
            'category': 'visa',
            'list_price': 50000.0,
            'standard_cost': 30000.0,
        })
        self.service_ticket = self.ServiceCatalog.create({
            'name': 'Flight Ticket Test',
            'code': 'TKT-TEST',
            'category': 'ticket',
            'list_price': 100000.0,
            'standard_cost': 85000.0,
        })

    def test_01_user_default_home_actions(self):
        """ Verify provisioned users have assigned default home actions """
        user_kamal = self.env.ref('alamia_travel_core.user_kamal')
        user_jawad = self.env.ref('alamia_travel_core.user_jawad')
        user_zeeshan = self.env.ref('alamia_travel_core.user_zeeshan')
        user_tayyab = self.env.ref('alamia_travel_core.user_tayyab')
        user_ali = self.env.ref('alamia_travel_core.user_ali')
        user_admin = self.env.ref('base.user_admin')


        self.assertTrue(user_kamal.action_id, "Kamal should have a default home action.")
        self.assertTrue(user_jawad.action_id, "Jawad should have a default home action.")
        self.assertTrue(user_zeeshan.action_id, "Zeeshan should have a default home action.")
        self.assertTrue(user_tayyab.action_id, "Tayyab should have a default home action.")
        self.assertTrue(user_ali.action_id, "Ali should have a default home action.")
        self.assertTrue(user_admin.action_id, "Admin should have a default home action.")


    def test_02_expense_management_workflow(self):
        """ Verify expense category creation, expense creation, approval, and posting """
        cat_office = self.ExpenseCategory.create({
            'name': 'Office Rent Test',
            'code': 'EXP_RENT_TEST',
        })
        expense = self.TravelExpense.create({
            'category_id': cat_office.id,
            'description': 'Monthly Office Rent Payment',
            'amount': 150000.0,
            'payment_method': 'bank',
        })
        self.assertEqual(expense.state, 'draft')
        self.assertEqual(expense.amount, 150000.0)

        expense.action_approve()
        self.assertEqual(expense.state, 'approved')

        expense.action_post()
        self.assertEqual(expense.state, 'posted')
        self.assertTrue(expense.move_id, "Posting an expense should generate an account.move bill entry.")

        expense.action_pay()
        self.assertEqual(expense.state, 'paid')

    def test_03_service_packages(self):
        """ Verify service package bundle creation and pricing aggregation """
        package = self.ServicePackage.create({
            'name': 'Umrah Package Test',
            'code': 'PKG-UMRAH-TEST',
            'line_ids': [
                (0, 0, {
                    'service_id': self.service_visa.id,
                    'quantity': 2.0,
                    'unit_price': 50000.0,
                    'cost_price': 30000.0,
                }),
                (0, 0, {
                    'service_id': self.service_ticket.id,
                    'quantity': 2.0,
                    'unit_price': 100000.0,
                    'cost_price': 85000.0,
                })
            ]
        })
        self.assertEqual(package.total_selling_price, 300000.0)
        self.assertEqual(package.total_cost_price, 230000.0)
        self.assertEqual(package.expected_profit, 70000.0)

    def test_04_subagent_commission_and_stats(self):
        """ Verify sub-agent commission calculation on sale line and partner stats """
        sale = self.TravelSale.create({
            'customer_id': self.customer.id,
            'line_ids': [(0, 0, {
                'service_id': self.service_ticket.id,
                'description': 'Ticket via SubAgent',
                'quantity': 1.0,
                'unit_price': 120000.0,
                'supplier_id': self.supplier.id,
                'cost_amount': 100000.0,
                'agent_id': self.agent.id,
                'commission_rate': 5.0,
            })]
        })
        line = sale.line_ids[0]
        self.assertEqual(line.commission_amount, 6000.0) # 120000 * 5%

        self.agent._compute_agent_stats()
        self.assertEqual(self.agent.total_agent_sales_count, 1)
        self.assertEqual(self.agent.total_agent_sales_amount, 120000.0)
        self.assertEqual(self.agent.total_agent_commission_amount, 6000.0)

    def test_05_register_payment_action(self):
        """ Verify payment registration action on travel.sale """
        sale = self.TravelSale.create({
            'customer_id': self.customer.id,
            'line_ids': [(0, 0, {
                'service_id': self.service_visa.id,
                'description': 'Visa Service',
                'quantity': 1.0,
                'unit_price': 50000.0,
            })]
        })
        sale.action_confirm()
        res = sale.action_register_payment()
        self.assertEqual(res.get('res_model'), 'account.payment.register')
        self.assertTrue(sale.invoice_ids, "Register payment action should automatically generate customer invoice.")

    def test_06_mandatory_activity_cockpit_acceptance_flow(self):
        """
        Acceptance Test:
        1. Admin assigns mail.activity on a customer to Tayyab.
        2. Tayyab fetches dashboard and sees activity under 'My Work Today'.
        3. Tayyab completes activity with outcome note & schedules follow-up.
        4. Activity is completed and new follow-up is scheduled.
        5. Manager team workload reflects updated workload state for Tayyab.
        """
        from datetime import date, timedelta
        today = date.today()
        user_tayyab = self.env.ref('alamia_travel_core.user_tayyab')
        act_type = self.env['mail.activity.type'].search([], limit=1)

        # 1. Admin creates activity for Tayyab
        partner_model_id = self.env['ir.model']._get_id('res.partner')
        activity = self.env['mail.activity'].create({
            'res_model_id': partner_model_id,
            'res_id': self.customer.id,
            'activity_type_id': act_type.id,
            'summary': 'Call Customer regarding outstanding payment',
            'date_deadline': today,
            'user_id': user_tayyab.id,
        })

        # 2. Tayyab fetches dashboard data
        Dashboard = self.env['travel.dashboard'].with_user(user_tayyab)
        data = Dashboard.get_dashboard_data('ops_marketing')

        initial_tayyab_workload = next((w for w in data['team_workload'] if w['user_id'] == user_tayyab.id), {'today_count': 0, 'upcoming_count': 0})
        initial_today = initial_tayyab_workload['today_count']
        initial_upcoming = initial_tayyab_workload['upcoming_count']

        act_today_ids = [a['id'] for a in data['my_activities']['today']]
        self.assertIn(activity.id, act_today_ids, "Assigned activity should appear in Tayyab's 'My Work Today'")

        # 3. Tayyab completes activity with outcome feedback & schedules next activity
        tomorrow = str(today + timedelta(days=1))
        Dashboard.action_complete_activity(
            activity_id=activity.id,
            outcome="Payment Promised",
            feedback="Customer promised transfer by tomorrow afternoon",
            next_activity={
                'activity_type_id': act_type.id,
                'date_deadline': tomorrow,
                'summary': 'Verify bank transfer receipt',
                'user_id': user_tayyab.id,
            }
        )

        # 4. Verify original activity completed and new activity created
        self.env.flush_all()
        self.assertFalse(self.env['mail.activity'].search([('id', '=', activity.id)]), "Completed activity should no longer exist in mail.activity table.")

        new_activity = self.env['mail.activity'].search([
            ('res_model', '=', 'res.partner'),
            ('res_id', '=', self.customer.id),
            ('user_id', '=', user_tayyab.id),
        ])
        self.assertEqual(len(new_activity), 1, "New follow-up activity should be scheduled.")
        self.assertEqual(new_activity.summary, 'Verify bank transfer receipt')
        self.assertEqual(str(new_activity.date_deadline), tomorrow)

        # 5. Verify manager workload matrix updates
        updated_data = Dashboard.get_dashboard_data('ops_marketing')
        tayyab_workload = next((w for w in updated_data['team_workload'] if w['user_id'] == user_tayyab.id), None)
        self.assertIsNotNone(tayyab_workload, "Tayyab should be present in team workload matrix.")
        self.assertEqual(tayyab_workload['today_count'], initial_today - 1)
        self.assertEqual(tayyab_workload['upcoming_count'], initial_upcoming + 1)

    def test_07_dynamic_dashboard_widget_permissions(self):
        """ Verify dynamic dashboard widget permissions matrix via ir.config_parameter """
        icp = self.env['ir.config_parameter'].sudo()

        # Disable sales_by_service for ops_marketing role and enable team_workload
        icp.set_param('alamia_travel.dashboard_show_sales_by_service_ops_marketing', 'False')
        icp.set_param('alamia_travel.dashboard_show_team_workload_ops_marketing', 'True')

        user_tayyab = self.env.ref('alamia_travel_core.user_tayyab')
        Dashboard = self.env['travel.dashboard'].with_user(user_tayyab)
        data = Dashboard.get_dashboard_data('ops_marketing')

        perms = data.get('widget_permissions', {})
        self.assertFalse(perms.get('sales_by_service'), "Sales by Service widget should be disabled for ops_marketing.")
        self.assertTrue(perms.get('team_workload'), "Team workload widget should be enabled for ops_marketing.")

        # Re-enable
        icp.set_param('alamia_travel.dashboard_show_sales_by_service_ops_marketing', 'True')
        data_updated = Dashboard.get_dashboard_data('ops_marketing')
        self.assertTrue(data_updated.get('widget_permissions', {}).get('sales_by_service'))

    def test_08_role_based_menu_visibility(self):
        """ Verify menu visibility security rules across user roles """
        user_tayyab = self.env.ref('alamia_travel_core.user_tayyab')
        user_kamal = self.env.ref('alamia_travel_core.user_kamal')
        user_ali = self.env.ref('alamia_travel_core.user_ali')

        menu_config = self.env.ref('alamia_travel_core.menu_travel_configuration')
        menu_finance = self.env.ref('alamia_travel_core.menu_travel_finance')
        menu_ops = self.env.ref('alamia_travel_core.menu_travel_operations')
        menu_dash_settings = self.env.ref('alamia_travel_reporting.menu_travel_dashboard_settings')

        all_menus = self.env['ir.ui.menu'].search([])

        # 1. Tayyab (Ops & Marketing) - Should see Operations, but NOT Configuration, Finance, or Dashboard Settings
        tayyab_visible = all_menus.with_user(user_tayyab)._filter_visible_menus()
        self.assertIn(menu_ops, tayyab_visible, "Tayyab should have access to Operations menu.")
        self.assertNotIn(menu_config, tayyab_visible, "Tayyab should NOT have access to Configuration menu.")
        
        self.assertNotIn(menu_finance, tayyab_visible, "Tayyab should NOT have access to Finance menu.")
        self.assertNotIn(menu_dash_settings, tayyab_visible, "Tayyab should NOT have access to Dashboard Settings menu.")

        # 2. Kamal (CEO) - Should see Operations, Finance, Reporting
        kamal_visible = all_menus.with_user(user_kamal)._filter_visible_menus()
        self.assertIn(menu_ops, kamal_visible, "Kamal should have access to Operations menu.")
        self.assertIn(menu_finance, kamal_visible, "Kamal should have access to Finance menu.")

        # 3. Ali (IT Director / Admin) - Should see all menus including Configuration and Dashboard Settings
        ali_visible = all_menus.with_user(user_ali)._filter_visible_menus()
        self.assertIn(menu_ops, ali_visible)
        self.assertIn(menu_config, ali_visible, "Ali should have access to Configuration menu.")
        self.assertIn(menu_finance, ali_visible, "Ali should have access to Finance menu.")
        self.assertIn(menu_dash_settings, ali_visible, "Ali should have access to Dashboard Settings menu.")

    def test_09_task_schedule_wizard_flow(self):
        """ Verify CEO/Manager can schedule and assign a task to staff via wizard """
        from datetime import date
        today = date.today()
        user_kamal = self.env.ref('alamia_travel_core.user_kamal')
        user_tayyab = self.env.ref('alamia_travel_core.user_tayyab')
        act_type = self.env['mail.activity.type'].search([], limit=1)

        wizard = self.env['travel.schedule.activity.wizard'].with_user(user_kamal).create({
            'user_id': user_tayyab.id,
            'activity_type_id': act_type.id,
            'summary': 'Urgent Visa Clearance Check',
            'date_deadline': today,
            'partner_id': self.customer.id,
            'note': 'Please verify visa approval with Saudi Ministry portal',
        })

        res = wizard.action_schedule_task()
        self.assertEqual(res.get('type'), 'ir.actions.client')

        # Verify activity created and assigned to Tayyab
        act = self.env['mail.activity'].search([
            ('res_model', '=', 'res.partner'),
            ('res_id', '=', self.customer.id),
            ('user_id', '=', user_tayyab.id),
            ('summary', '=', 'Urgent Visa Clearance Check'),
        ])
        self.assertTrue(act.exists(), "Activity should be created and assigned to Tayyab.")

    def test_10_financial_data_scoping_per_role(self):
        """ Verify financial data scoping: CEO sees financial metrics; Ops/Marketing is stripped """
        user_kamal = self.env.ref('alamia_travel_core.user_kamal')
        user_tayyab = self.env.ref('alamia_travel_core.user_tayyab')

        Dashboard = self.env['travel.dashboard']

        # CEO Dashboard Payload
        ceo_data = Dashboard.with_user(user_kamal).get_dashboard_data('ceo')
        self.assertTrue(ceo_data.get('is_financial_role'), "CEO should be identified as financial role.")

        # Tayyab (Ops & Marketing) Dashboard Payload
        tayyab_data = Dashboard.with_user(user_tayyab).get_dashboard_data('ops_marketing')
        self.assertFalse(tayyab_data.get('is_financial_role'), "Ops & Marketing should NOT be identified as financial role.")
        self.assertEqual(tayyab_data['kpis'].get('monthly_gross_profit'), 0.0, "Gross profit must be stripped for non-financial roles.")
        self.assertEqual(tayyab_data['kpis'].get('cash_position'), 0.0, "Cash position must be stripped for non-financial roles.")
        self.assertEqual(tayyab_data.get('sales_by_service'), [], "Sales by service list must be empty for non-financial roles.")
