from odoo import api, fields, models, _
from odoo.exceptions import UserError

class TravelSale(models.Model):
    _inherit = 'travel.sale'

    invoice_ids = fields.One2many('account.move', 'travel_sale_id', string='Invoices/Bills')
    invoice_count = fields.Integer(string='Invoice Count', compute='_compute_invoice_count')
    bill_count = fields.Integer(string='Bill Count', compute='_compute_invoice_count')

    amount_invoiced = fields.Monetary(string='Amount Invoiced', compute='_compute_financial_status', store=True)
    amount_due = fields.Monetary(string='Amount Due', compute='_compute_financial_status', store=True)

    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overpaid', 'Overpaid')
    ], string='Payment Status', compute='_compute_financial_status', store=True)

    @api.depends('invoice_ids.state', 'invoice_ids.payment_state', 'invoice_ids.amount_total', 'invoice_ids.amount_residual')
    def _compute_financial_status(self):
        for sale in self:
            invoices = sale.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted')
            
            amount_invoiced = sum(invoices.mapped('amount_total'))
            amount_due = sum(invoices.mapped('amount_residual'))
            
            sale.amount_invoiced = amount_invoiced
            sale.amount_due = amount_due
            
            if not invoices:
                sale.payment_status = 'unpaid'
            elif amount_due == 0 and amount_invoiced > 0:
                sale.payment_status = 'paid'
            elif amount_due < 0:
                sale.payment_status = 'overpaid'
            elif amount_due < amount_invoiced:
                sale.payment_status = 'partial'
            else:
                sale.payment_status = 'unpaid'

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for sale in self:
            sale.invoice_count = len(sale.invoice_ids.filtered(lambda m: m.move_type == 'out_invoice'))
            sale.bill_count = len(sale.invoice_ids.filtered(lambda m: m.move_type == 'in_invoice'))

    def action_view_invoices(self):
        self.ensure_one()
        invoices = self.invoice_ids.filtered(lambda m: m.move_type == 'out_invoice')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action['domain'] = [('id', 'in', invoices.ids)]
        action['context'] = {'default_move_type': 'out_invoice', 'default_travel_sale_id': self.id}
        return action

    def action_view_bills(self):
        self.ensure_one()
        bills = self.invoice_ids.filtered(lambda m: m.move_type == 'in_invoice')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_invoice_type")
        action['domain'] = [('id', 'in', bills.ids)]
        action['context'] = {'default_move_type': 'in_invoice', 'default_travel_sale_id': self.id}
        return action

    def action_create_invoice(self):
        self.ensure_one()
        if self.state not in ['confirmed', 'in_progress', 'completed']:
            raise UserError(_("You can only create an invoice for a confirmed sale."))
        
        invoice_lines = []
        for line in self.line_ids:
            if line.selling_amount > 0:
                if not line.service_id.income_account_id:
                    raise UserError(_("Please define an Income Account for service: %s", line.service_id.name))
                
                invoice_lines.append((0, 0, {
                    'name': line.description,
                    'quantity': line.quantity,
                    'price_unit': line.unit_price,
                    'account_id': line.service_id.income_account_id.id,
                }))

        if not invoice_lines:
            raise UserError(_("There are no lines with a selling amount to invoice."))

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'invoice_date': fields.Date.context_today(self),
            'travel_sale_id': self.id,
            'invoice_line_ids': invoice_lines,
        }

        invoice = self.env['account.move'].create(invoice_vals)
        return self.action_view_invoices()

    def action_create_vendor_bills(self):
        self.ensure_one()
        if self.state not in ['confirmed', 'in_progress', 'completed']:
            raise UserError(_("You can only create vendor bills for a confirmed sale."))
        
        # Group lines by supplier
        supplier_lines = {}
        for line in self.line_ids:
            if line.cost_amount > 0 and line.supplier_id:
                if line.supplier_id not in supplier_lines:
                    supplier_lines[line.supplier_id] = []
                supplier_lines[line.supplier_id].append(line)

        if not supplier_lines:
            raise UserError(_("There are no lines with a supplier and cost amount to bill."))

        created_bills = []
        for supplier, lines in supplier_lines.items():
            bill_lines = []
            for line in lines:
                if not line.service_id.expense_account_id:
                    raise UserError(_("Please define an Expense Account for service: %s", line.service_id.name))
                bill_lines.append((0, 0, {
                    'name': f"{self.name} - {line.description}",
                    'quantity': 1, # supplier cost is total cost
                    'price_unit': line.cost_amount,
                    'account_id': line.service_id.expense_account_id.id,
                }))

            bill_vals = {
                'move_type': 'in_invoice',
                'partner_id': supplier.id,
                'invoice_date': fields.Date.context_today(self),
                'travel_sale_id': self.id,
                'invoice_line_ids': bill_lines,
            }
            bill = self.env['account.move'].create(bill_vals)
            created_bills.append(bill)

        return self.action_view_bills()
