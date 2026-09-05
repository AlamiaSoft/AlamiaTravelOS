from odoo import models, fields

class ServiceCatalog(models.Model):
    _name = 'travel.service.catalog'
    _description = 'Travel Service Catalog'
    _order = 'sequence, name'

    name = fields.Char('Service Name', required=True)
    code = fields.Char('Code', required=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', default=10)
    description = fields.Text('Description')

    # Accounts for finance integration (Sprint 3/4)
    income_account_id = fields.Many2one(
        'account.account',
        string="Income Account",
        company_dependent=True,
        domain="[('account_type', '=', 'income')]"
    )
    expense_account_id = fields.Many2one(
        'account.account',
        string="Expense Account",
        company_dependent=True,
        domain="[('account_type', '=', 'expense')]"
    )
