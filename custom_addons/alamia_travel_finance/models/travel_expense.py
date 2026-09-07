# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class TravelExpenseCategory(models.Model):
    _name = 'travel.expense.category'
    _description = 'Travel OS Expense Category'
    _order = 'sequence, name'

    name = fields.Char(string='Category Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    account_id = fields.Many2one(
        'account.account',
        string='Default Expense Account',
        domain="[('account_type', '=', 'expense')]"
    )
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string='Description')
    expense_count = fields.Integer(string='Expense Count', compute='_compute_expense_count')

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'The category code must be unique!'),
    ]

    def _compute_expense_count(self):
        for rec in self:
            rec.expense_count = self.env['travel.expense'].search_count([('category_id', '=', rec.id)])


class TravelExpense(models.Model):
    _name = 'travel.expense'
    _description = 'Travel OS Expense Entry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Expense Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    category_id = fields.Many2one('travel.expense.category', string='Category', required=True, tracking=True)
    date = fields.Date(string='Expense Date', required=True, default=fields.Date.context_today, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Payee / Vendor', tracking=True)
    description = fields.Char(string='Description / Purpose', required=True, tracking=True)
    amount = fields.Monetary(string='Amount', required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('online', 'Online Payment / Card'),
        ('other', 'Other')
    ], string='Payment Method', default='cash', required=True, tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)

    user_id = fields.Many2one('res.users', string='Recorded By', default=lambda self: self.env.user, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    notes = fields.Text(string='Internal Notes')
    move_id = fields.Many2one('account.move', string='Journal Entry / Bill', readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('travel.expense') or _('New')
        return super().create(vals_list)

    def action_approve(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only draft expenses can be approved."))
            rec.state = 'approved'

    def action_post(self):
        for rec in self:
            if rec.state not in ('draft', 'approved'):
                raise UserError(_("Expense must be draft or approved to post."))
            if not rec.move_id:
                account = rec.category_id.account_id
                if not account:
                    account = self.env['account.account'].search([('account_type', '=', 'expense')], limit=1)
                partner = rec.partner_id or self.env.user.company_id.partner_id
                journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
                if account and journal:
                    move = self.env['account.move'].create({
                        'move_type': 'in_invoice',
                        'partner_id': partner.id,
                        'invoice_date': rec.date,
                        'ref': rec.name + ' - ' + (rec.description or ''),
                        'journal_id': journal.id,
                        'invoice_line_ids': [(0, 0, {
                            'name': rec.description or rec.category_id.name,
                            'quantity': 1.0,
                            'price_unit': rec.amount,
                            'account_id': account.id,
                        })]
                    })
                    rec.move_id = move.id
            rec.state = 'posted'

    def action_pay(self):
        for rec in self:
            if rec.state != 'posted':
                rec.action_post()
            rec.state = 'paid'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'
