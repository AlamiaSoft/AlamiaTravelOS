# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError, MissingError, UserError


class TestAlamiaTravelsAi(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Partner = self.env['res.partner']
        self.TravelSale = self.env['travel.sale']
        self.TravelSaleLine = self.env['travel.sale.line']
        self.ServiceCatalog = self.env['travel.service.catalog']

        # Setup test customer & supplier
        self.customer = self.Partner.create({
            'name': 'Syed Kamal Ahmed Test AI',
            'is_travel_customer': True,
            'phone': '+923001234567',
        })
        self.supplier = self.Partner.create({
            'name': 'Saudi Airlines Test AI',
            'is_travel_supplier': True,
        })

        # Setup service catalog item
        self.service_cat = self.ServiceCatalog.create({
            'name': '14-Day Umrah Package Category',
            'code': 'UMR-14D-AI',
            'category': 'package',
            'list_price': 150000.0,
            'standard_cost': 110000.0,
        })

        # Setup test booking
        self.booking = self.TravelSale.create({
            'customer_id': self.customer.id,
            'state': 'confirmed',
        })
        self.line = self.TravelSaleLine.create({
            'sale_id': self.booking.id,
            'service_id': self.service_cat.id,
            'description': '14-Day Umrah Package Line',
            'quantity': 1.0,
            'unit_price': 150000.0,
            'cost_amount': 110000.0,
        })

        # Setup users for roles
        self.user_kamal = self.env.ref('alamia_travel_core.user_kamal', raise_if_not_found=False) or self.env.ref('base.user_admin')
        self.user_tayyab = self.env.ref('alamia_travel_core.user_tayyab', raise_if_not_found=False) or self.env.ref('base.user_admin')

        # MCP Mixin
        self.mcp_mixin = self.env['mcp.mixin']

    def test_01_employee_profile_bootstrap(self):
        """ Test get_employee_profile returns complete role profile and allowed tools """
        res = self.mcp_mixin.with_user(self.user_kamal).get_employee_profile()
        payload = res.get('structuredContent', {})

        self.assertIn('user', payload)
        self.assertIn('role_profile', payload)
        self.assertIn('allowed_skills', payload)
        self.assertIn('allowed_tools', payload)

        self.assertEqual(payload['user']['id'], self.user_kamal.id)
        self.assertTrue(len(payload['allowed_skills']) > 0, "Role should have allowed skills.")
        self.assertIn('get_customer_360', payload['allowed_tools'])

    def test_02_customer_360_facts(self):
        """ Test get_customer_360 returns structured customer facts """
        res = self.mcp_mixin.with_user(self.user_kamal).get_customer_360(partner_id=self.customer.id)
        payload = res.get('structuredContent', {})

        self.assertIn('customer', payload)
        self.assertEqual(payload['customer']['id'], self.customer.id)
        self.assertEqual(payload['customer']['name'], 'Syed Kamal Ahmed Test AI')
        self.assertIn('metrics', payload)
        self.assertEqual(payload['metrics']['total_bookings_count'], 1)
        self.assertEqual(payload['metrics']['lifetime_spent'], 150000.0)

    def test_03_booking_360_and_profitability(self):
        """ Test get_booking_360 and get_booking_profitability facts """
        # Booking 360
        res_360 = self.mcp_mixin.with_user(self.user_kamal).get_booking_360(booking_id=self.booking.id)
        payload_360 = res_360.get('structuredContent', {})
        self.assertEqual(payload_360['booking']['id'], self.booking.id)
        self.assertEqual(payload_360['financials']['amount_total'], 150000.0)

        # Booking Profitability
        res_prof = self.mcp_mixin.with_user(self.user_kamal).get_booking_profitability(booking_id=self.booking.id)
        payload_prof = res_prof.get('structuredContent', {})

        self.assertIn('profitability', payload_prof)
        self.assertEqual(payload_prof['profitability']['revenue'], 150000.0)
        self.assertEqual(payload_prof['profitability']['total_supplier_cost'], 110000.0)
        self.assertEqual(payload_prof['profitability']['gross_profit'], 40000.0)
        self.assertIn('cost_lines', payload_prof)

    def test_04_work_items(self):
        """ Test get_work_items returns open activities """
        # Create an activity for test user
        model_id = self.env['ir.model']._get_id('res.partner')
        self.env['mail.activity'].sudo().create({
            'res_model': 'res.partner',
            'res_model_id': model_id,
            'res_id': self.customer.id,
            'summary': 'Test AI Follow-up Activity',
            'user_id': self.user_kamal.id,
        })

        res = self.mcp_mixin.with_user(self.user_kamal).get_work_items(urgency='all')
        payload = res.get('structuredContent', {})

        self.assertIn('items', payload)
        self.assertTrue(len(payload['items']) > 0)
        self.assertEqual(payload['items'][0]['summary'], 'Test AI Follow-up Activity')

    def test_05_propose_and_create_followup(self):
        """ Test propose_action and create_followup with chatter audit & idempotency key """
        idemp_key = 'IDEMP-TEST-001'
        res = self.mcp_mixin.with_user(self.user_kamal).create_followup(
            res_model='res.partner',
            res_id=self.customer.id,
            summary='Call Customer for Umrah Documents',
            note='Urgent visa application passport required',
            idempotency_key=idemp_key,
        )
        payload = res.get('structuredContent', {})
        self.assertEqual(payload['status'], 'COMPLETED')

        # Test Idempotency duplicate execution
        res_dup = self.mcp_mixin.with_user(self.user_kamal).create_followup(
            res_model='res.partner',
            res_id=self.customer.id,
            summary='Call Customer for Umrah Documents',
            idempotency_key=idemp_key,
        )
        self.assertIn('previously executed', res_dup['content'][0]['text'])

    def test_06_security_enforcement(self):
        """ Test backend authorization denies unauthorized action types per role """
        from odoo.addons.mcp_server.models.alamia_ai_actions import ActionStateMachine

        # Sales Assistant attempting post_invoice should be DENIED
        with self.assertRaises(AccessError):
            ActionStateMachine.validate_action_authorization(
                user=self.user_tayyab,
                role_id='sales_assistant',
                action_type='post_invoice',
            )
