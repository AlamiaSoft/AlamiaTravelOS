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

        self.assertTrue(user_kamal.action_id, "Kamal should have a default home action.")
        self.assertTrue(user_jawad.action_id, "Jawad should have a default home action.")
        self.assertTrue(user_zeeshan.action_id, "Zeeshan should have a default home action.")
        self.assertTrue(user_tayyab.action_id, "Tayyab should have a default home action.")
        self.assertTrue(user_ali.action_id, "Ali should have a default home action.")

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
