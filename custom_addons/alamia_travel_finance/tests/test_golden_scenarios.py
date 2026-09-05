from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class TestGoldenScenarios(TransactionCase):

    def setUp(self):
        super(TestGoldenScenarios, self).setUp()
        
        self.company = self.env.company
        
        # Accounts
        self.income_account = self.env['account.account'].create({
            'name': 'Travel Income',
            'code': '400100',
            'account_type': 'income',
            'company_ids': [(4, self.company.id)],
        })
        self.expense_account = self.env['account.account'].create({
            'name': 'Travel Cost of Sales',
            'code': '500100',
            'account_type': 'expense',
            'company_ids': [(4, self.company.id)],
        })
        
        # Partners
        self.customer = self.env['res.partner'].create({
            'name': 'Ahmed Khan',
            'is_travel_customer': True,
        })
        self.vendor = self.env['res.partner'].create({
            'name': 'Vendor A',
            'is_travel_supplier': True,
        })
        
        # Service
        self.service_ticket = self.env['travel.service.catalog'].create({
            'name': 'Ticket',
            'code': 'TKT',
            'income_account_id': self.income_account.id,
            'expense_account_id': self.expense_account.id,
        })
        
        # Journals
        self.bank_journal = self.env['account.journal'].search([('type', '=', 'bank'), ('company_id', '=', self.company.id)], limit=1)
        if not self.bank_journal:
            self.bank_journal = self.env['account.journal'].create({
                'name': 'Bank',
                'type': 'bank',
                'code': 'BNK',
                'company_id': self.company.id,
            })

    def test_01_golden_scenario_1(self):
        """
        1. Single Sale (150,000 selling, 120,000 cost)
        Expected: Revenue = 150k, Cost = 120k, Gross Profit = 30k
        """
        sale = self.env['travel.sale'].create({
            'customer_id': self.customer.id,
            'line_ids': [(0, 0, {
                'service_id': self.service_ticket.id,
                'description': 'Dubai Ticket',
                'quantity': 1,
                'unit_price': 150000,
                'supplier_id': self.vendor.id,
                'cost_amount': 120000,
            })]
        })
        
        sale.action_confirm()
        
        self.assertEqual(sale.total_selling_amount, 150000)
        self.assertEqual(sale.total_cost_amount, 120000)
        self.assertEqual(sale.gross_profit, 30000)
        
        # Create invoices and verify accounting balances
        sale.action_create_invoice()
        sale.action_create_vendor_bills()
        
        # Post invoices
        for inv in sale.invoice_ids:
            inv.action_post()
            
        self.assertEqual(sale.amount_invoiced, 150000)
        self.assertEqual(sale.amount_due, 150000)
        self.assertEqual(sale.payment_status, 'unpaid')

    def test_02_golden_scenario_2(self):
        """
        2. Multiple Payments (Sale 200,000, Cost 150,000)
        Payments: 50k, 70k, 80k.
        Expected: Paid = 200,000, Outstanding = 0, Gross Profit = 50,000
        """
        sale = self.env['travel.sale'].create({
            'customer_id': self.customer.id,
            'line_ids': [(0, 0, {
                'service_id': self.service_ticket.id,
                'description': 'Umrah Package',
                'quantity': 1,
                'unit_price': 200000,
                'supplier_id': self.vendor.id,
                'cost_amount': 150000,
            })]
        })
        sale.action_confirm()
        sale.action_create_invoice()
        
        invoice = sale.invoice_ids[0]
        invoice.action_post()
        
        # Pay 50k
        self.env['account.payment.register'].with_context(active_model='account.move', active_ids=invoice.ids).create({
            'amount': 50000,
            'journal_id': self.bank_journal.id,
        })._create_payments()
        
        sale._compute_financial_status()
        self.assertEqual(sale.payment_status, 'partial')
        self.assertEqual(sale.amount_due, 150000)
        
        # Pay 70k
        self.env['account.payment.register'].with_context(active_model='account.move', active_ids=invoice.ids).create({
            'amount': 70000,
            'journal_id': self.bank_journal.id,
        })._create_payments()
        
        sale._compute_financial_status()
        self.assertEqual(sale.amount_due, 80000)

        # Pay 80k
        self.env['account.payment.register'].with_context(active_model='account.move', active_ids=invoice.ids).create({
            'amount': 80000,
            'journal_id': self.bank_journal.id,
        })._create_payments()
        
        sale._compute_financial_status()
        self.assertEqual(sale.amount_due, 0)
        self.assertEqual(sale.payment_status, 'paid')
        self.assertEqual(sale.gross_profit, 50000)

    def test_03_golden_scenario_3_customer_balance(self):
        """
        3. Multiple Sales / Customer Balance
        Sales: 100,000, 200,000, 50,000
        Payments: 100,000, 50,000
        Expected: Total Sales = 350,000, Paid = 150,000, Outstanding = 200,000
        """
        sales = []
        for amount in [100000, 200000, 50000]:
            sale = self.env['travel.sale'].create({
                'customer_id': self.customer.id,
                'line_ids': [(0, 0, {
                    'service_id': self.service_ticket.id,
                    'description': 'Flight',
                    'quantity': 1,
                    'unit_price': amount,
                })]
            })
            sale.action_confirm()
            sale.action_create_invoice()
            sale.invoice_ids.action_post()
            sales.append(sale)
            
        invoices = self.env['account.move'].search([('travel_sale_id', 'in', [s.id for s in sales])])
        invoices = sorted(invoices, key=lambda i: i.amount_total, reverse=True) # 200k, 100k, 50k
        
        # Pay 100k against 200k invoice
        self.env['account.payment.register'].with_context(active_model='account.move', active_ids=[invoices[0].id]).create({
            'amount': 100000,
            'journal_id': self.bank_journal.id,
        })._create_payments()
        
        # Pay 50k against 100k invoice
        self.env['account.payment.register'].with_context(active_model='account.move', active_ids=[invoices[1].id]).create({
            'amount': 50000,
            'journal_id': self.bank_journal.id,
        })._create_payments()
        
        self.env.invalidate_all()
        
        # Actually in Odoo it's simply the sum of amount_residual on out_invoice
        customer_due = sum(self.env['account.move'].search([('partner_id', '=', self.customer.id), ('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]).mapped('amount_residual'))
        self.assertEqual(customer_due, 200000)

    def test_04_golden_scenario_4_supplier_balance(self):
        """
        4. Supplier Balance
        Cost: 100k, 50k, 75k. Total payable = 225k
        Payments: 100k, 50k
        Expected: Outstanding = 75,000
        """
        sale = self.env['travel.sale'].create({
            'customer_id': self.customer.id,
            'line_ids': [
                (0, 0, {'service_id': self.service_ticket.id, 'description': 'T1', 'quantity': 1, 'unit_price': 150000, 'supplier_id': self.vendor.id, 'cost_amount': 100000}),
                (0, 0, {'service_id': self.service_ticket.id, 'description': 'T2', 'quantity': 1, 'unit_price': 75000, 'supplier_id': self.vendor.id, 'cost_amount': 50000}),
                (0, 0, {'service_id': self.service_ticket.id, 'description': 'T3', 'quantity': 1, 'unit_price': 100000, 'supplier_id': self.vendor.id, 'cost_amount': 75000}),
            ]
        })
        sale.action_confirm()
        sale.action_create_vendor_bills()
        
        bills = sale.invoice_ids.filtered(lambda m: m.move_type == 'in_invoice')
        self.assertEqual(len(bills), 1) # grouped into 1 bill
        bills.action_post()
        
        self.assertEqual(bills.amount_total, 225000)
        
        # Pay 150,000 (100k + 50k)
        self.env['account.payment.register'].with_context(active_model='account.move', active_ids=bills.ids).create({
            'amount': 150000,
            'journal_id': self.bank_journal.id,
        })._create_payments()
        
        supplier_due = sum(self.env['account.move'].search([('partner_id', '=', self.vendor.id), ('move_type', '=', 'in_invoice'), ('state', '=', 'posted')]).mapped('amount_residual'))
        self.assertEqual(supplier_due, 75000)

    def test_05_golden_scenario_5_profitability(self):
        """
        5. Profitability
        Ticket A: Rev 150k, Cost 120k
        Visa B: Rev 50k, Cost 20k
        Hotel C: Rev 100k, Cost 70k
        Expected: Total Revenue = 300,000, Total Cost = 210,000, Gross Profit = 90,000
        """
        service_visa = self.env['travel.service.catalog'].create({
            'name': 'Visa',
            'code': 'VIS',
            'income_account_id': self.income_account.id,
            'expense_account_id': self.expense_account.id,
        })
        service_hotel = self.env['travel.service.catalog'].create({
            'name': 'Hotel',
            'code': 'HTL',
            'income_account_id': self.income_account.id,
            'expense_account_id': self.expense_account.id,
        })
        
        sale = self.env['travel.sale'].create({
            'customer_id': self.customer.id,
            'line_ids': [
                (0, 0, {'service_id': self.service_ticket.id, 'description': 'Ticket A', 'quantity': 1, 'unit_price': 150000, 'cost_amount': 120000}),
                (0, 0, {'service_id': service_visa.id, 'description': 'Visa B', 'quantity': 1, 'unit_price': 50000, 'cost_amount': 20000}),
                (0, 0, {'service_id': service_hotel.id, 'description': 'Hotel C', 'quantity': 1, 'unit_price': 100000, 'cost_amount': 70000}),
            ]
        })
        
        self.assertEqual(sale.total_selling_amount, 300000)
        self.assertEqual(sale.total_cost_amount, 210000)
        self.assertEqual(sale.gross_profit, 90000)
