from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)


class TestUsersRolesAndDashboards(TransactionCase):
    """
    Sprint: Kamal Express Users, Roles & Dashboards
    Acceptance Tests (automated)
    """

    def setUp(self):
        super().setUp()

        # Fetch the 5 provisioned users
        User = self.env['res.users'].sudo()
        self.user_kamal = User.search([('login', '=', 'kamal@kamalexpress.com')], limit=1)
        self.user_jawad = User.search([('login', '=', 'jawad@kamalexpress.com')], limit=1)
        self.user_ali = User.search([('login', '=', 'ali@kamalexpress.com')], limit=1)
        self.user_tayyab = User.search([('login', '=', 'tayyab@kamalexpress.com')], limit=1)
        self.user_zeeshan = User.search([('login', '=', 'zeeshan@kamalexpress.com')], limit=1)

        # Minimal test fixtures
        self.income_account = self.env['account.account'].search([('account_type', '=', 'income')], limit=1)
        self.expense_account = self.env['account.account'].search([('account_type', '=', 'expense')], limit=1)

        self.test_customer = self.env['res.partner'].sudo().create({
            'name': 'Test Customer ACL',
            'is_travel_customer': True,
        })
        self.test_service = self.env['travel.service.catalog'].sudo().create({
            'name': 'Test Ticket ACL',
            'code': 'TACLTEST',
            'income_account_id': self.income_account.id,
            'expense_account_id': self.expense_account.id,
        })

    # ------------------------------------------------------------------
    # 1. User Provisioning
    # ------------------------------------------------------------------
    def test_01_all_five_users_exist(self):
        """All 5 Kamal Express users must be provisioned."""
        self.assertTrue(self.user_kamal, "Syed Kamal Ahmed must exist")
        self.assertTrue(self.user_jawad, "Malik Jawad must exist")
        self.assertTrue(self.user_ali, "Ali Raza must exist")
        self.assertTrue(self.user_tayyab, "Tayyab must exist")
        self.assertTrue(self.user_zeeshan, "Zeeshan must exist")

    def test_02_correct_logins(self):
        """Users must use specified email addresses as logins."""
        self.assertEqual(self.user_kamal.login, 'kamal@kamalexpress.com')
        self.assertEqual(self.user_jawad.login, 'jawad@kamalexpress.com')
        self.assertEqual(self.user_ali.login, 'ali@kamalexpress.com')
        self.assertEqual(self.user_tayyab.login, 'tayyab@kamalexpress.com')
        self.assertEqual(self.user_zeeshan.login, 'zeeshan@kamalexpress.com')

    def test_03_correct_role_groups(self):
        """Each user must be in their correct organizational role group."""
        def has_group(user, xml_id):
            return user.has_group(xml_id)

        self.assertTrue(has_group(self.user_kamal, 'alamia_travel_core.travel_role_ceo'), "Kamal must be CEO")
        self.assertTrue(has_group(self.user_jawad, 'alamia_travel_core.travel_role_operations_director'), "Jawad must be Ops Director")
        self.assertTrue(has_group(self.user_ali, 'alamia_travel_core.travel_role_it_director'), "Ali must be IT Director")
        self.assertTrue(has_group(self.user_tayyab, 'alamia_travel_core.travel_role_operations_marketing'), "Tayyab must be Ops & Marketing")
        self.assertTrue(has_group(self.user_zeeshan, 'alamia_travel_core.travel_role_sales_director'), "Zeeshan must be Sales Director")

    # ------------------------------------------------------------------
    # 2. Sales Access
    # ------------------------------------------------------------------
    def _create_test_sale(self, user):
        """Helper: create a travel.sale as a specific user."""
        env_as_user = self.env['travel.sale'].with_user(user)
        return env_as_user.create({
            'customer_id': self.test_customer.id,
            'salesperson_id': user.id,
            'line_ids': [(0, 0, {
                'service_id': self.test_service.id,
                'description': f'Test sale as {user.name}',
                'quantity': 1,
                'unit_price': 10000,
            })]
        })

    def test_04_ceo_can_create_sale(self):
        """CEO must be able to create a travel sale."""
        sale = self._create_test_sale(self.user_kamal)
        self.assertTrue(sale.id, "CEO should be able to create a sale")

    def test_05_ops_director_can_create_sale(self):
        """Operations Director must be able to create a travel sale."""
        sale = self._create_test_sale(self.user_jawad)
        self.assertTrue(sale.id, "Operations Director should be able to create a sale")

    def test_06_ops_marketing_can_create_sale(self):
        """Assistant Ops & Marketing must be able to create a travel sale."""
        sale = self._create_test_sale(self.user_tayyab)
        self.assertTrue(sale.id, "Tayyab (Ops & Marketing) should be able to create a sale")

    def test_07_sales_director_can_create_sale(self):
        """Sales Director must be able to create a travel sale."""
        sale = self._create_test_sale(self.user_zeeshan)
        self.assertTrue(sale.id, "Zeeshan (Sales Director) should be able to create a sale")

    # ------------------------------------------------------------------
    # 3. Security: IT Director does NOT bypass accounting
    # ------------------------------------------------------------------
    def test_08_it_director_has_admin_groups(self):
        """Ali (IT Director) must have system admin group."""
        self.assertTrue(
            self.user_ali.has_group('base.group_system') or
            self.user_ali.has_group('base.group_erp_manager'),
            "IT Director must have admin/technical access"
        )

    def test_09_sales_users_do_not_have_system_admin(self):
        """Tayyab and Zeeshan must NOT have base.group_system admin access."""
        self.assertFalse(
            self.user_tayyab.has_group('base.group_system'),
            "Tayyab (Ops/Marketing) should not have system administration"
        )
        self.assertFalse(
            self.user_zeeshan.has_group('base.group_system'),
            "Zeeshan (Sales Director) should not have system administration"
        )

    def test_10_sales_director_has_invoicing(self):
        """Zeeshan must have Invoicing access."""
        self.assertTrue(
            self.user_zeeshan.has_group('account.group_account_invoice'),
            "Sales Director needs invoicing group to create and view invoices"
        )

    def test_11_ops_marketing_has_invoicing(self):
        """Tayyab must have Invoicing access."""
        self.assertTrue(
            self.user_tayyab.has_group('account.group_account_invoice'),
            "Ops & Marketing needs invoicing group"
        )

    # ------------------------------------------------------------------
    # 4. Dashboard Service: Role Authorization
    # ------------------------------------------------------------------
    def test_12_ceo_dashboard_service_returns_data(self):
        """CEO should get full executive dashboard data."""
        dashboard_env = self.env['travel.dashboard'].with_user(self.user_kamal)
        data = dashboard_env.get_dashboard_data(role='ceo')
        self.assertEqual(data['role'], 'ceo')
        self.assertIn('kpis', data)
        self.assertIn('monthly_sales', data['kpis'])
        self.assertIn('total_receivables', data['kpis'])
        self.assertIn('total_payables', data['kpis'])
        self.assertIn('cash_position', data['kpis'])
        self.assertIn('bank_position', data['kpis'])

    def test_13_ops_director_dashboard_service_returns_data(self):
        """Operations Director should get operations dashboard data."""
        dashboard_env = self.env['travel.dashboard'].with_user(self.user_jawad)
        data = dashboard_env.get_dashboard_data(role='operations')
        self.assertEqual(data['role'], 'operations')
        self.assertIn('kpis', data)
        self.assertIn('pending_transactions_count', data['kpis'])

    def test_14_sales_director_dashboard_service_returns_data(self):
        """Sales Director should get sales dashboard data."""
        dashboard_env = self.env['travel.dashboard'].with_user(self.user_zeeshan)
        data = dashboard_env.get_dashboard_data(role='sales')
        self.assertEqual(data['role'], 'sales')
        self.assertIn('outstanding_customers', data)

    def test_15_ops_marketing_dashboard_service_returns_data(self):
        """Ops & Marketing should get their dedicated dashboard data."""
        dashboard_env = self.env['travel.dashboard'].with_user(self.user_tayyab)
        data = dashboard_env.get_dashboard_data(role='ops_marketing')
        self.assertEqual(data['role'], 'ops_marketing')
        self.assertIn('kpis', data)

    def test_16_sales_director_cannot_access_ceo_dashboard(self):
        """Zeeshan (Sales Director) must NOT be able to request CEO role dashboard."""
        dashboard_env = self.env['travel.dashboard'].with_user(self.user_zeeshan)
        with self.assertRaises(AccessError, msg="Sales Director should not access CEO dashboard"):
            dashboard_env.get_dashboard_data(role='ceo')

    def test_17_ops_marketing_cannot_access_ceo_dashboard(self):
        """Tayyab must NOT be able to request the CEO role dashboard."""
        dashboard_env = self.env['travel.dashboard'].with_user(self.user_tayyab)
        with self.assertRaises(AccessError, msg="Ops/Marketing should not access CEO dashboard"):
            dashboard_env.get_dashboard_data(role='ceo')

    # ------------------------------------------------------------------
    # 5. Data consistency: sale figures match
    # ------------------------------------------------------------------
    def test_18_dashboard_data_is_consistent_with_reports(self):
        """Dashboard KPIs must match direct ORM aggregations."""
        # Create a known sale as Zeeshan
        sale = self._create_test_sale(self.user_zeeshan)
        sale.sudo().action_confirm()

        # Dashboard data as CEO (full visibility)
        dashboard_env = self.env['travel.dashboard'].with_user(self.user_kamal)
        data = dashboard_env.get_dashboard_data(role='ceo')

        # Direct ORM count of confirmed+draft+in_progress
        pending_direct = self.env['travel.sale'].sudo().search_count([
            ('state', 'in', ['draft', 'confirmed', 'in_progress'])
        ])
        self.assertEqual(data['kpis']['pending_transactions_count'], pending_direct,
                         "Dashboard pending count must match direct query")
