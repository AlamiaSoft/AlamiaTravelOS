from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class TravelSale(models.Model):
    _name = 'travel.sale'
    _description = 'Travel Sale'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_sale desc, id desc'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string='Customer', required=True, domain="[('is_travel_customer', '=', True)]", tracking=True)
    salesperson_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user, required=True, tracking=True)
    branch_id = fields.Many2one('res.company', string='Branch', default=lambda self: self.env.company, required=True, tracking=True)
    
    date_sale = fields.Date(string='Sale Date', default=fields.Date.context_today, required=True, tracking=True)
    external_ref = fields.Char(string='External Ref (Jotform)', help='Original Jotform Submission ID if migrated')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True, copy=False)

    line_ids = fields.One2many('travel.sale.line', 'sale_id', string='Sale Lines')

    # Financial Totals
    currency_id = fields.Many2one('res.currency', related='branch_id.currency_id', store=True)
    total_selling_amount = fields.Monetary(string='Total Selling', compute='_compute_totals', store=True, tracking=True)
    total_cost_amount = fields.Monetary(string='Total Cost', compute='_compute_totals', store=True)
    gross_profit = fields.Monetary(string='Gross Profit', compute='_compute_totals', store=True)

    @api.depends('line_ids.selling_amount', 'line_ids.cost_amount')
    def _compute_totals(self):
        for sale in self:
            total_selling = sum(line.selling_amount for line in sale.line_ids)
            total_cost = sum(line.cost_amount for line in sale.line_ids)
            sale.total_selling_amount = total_selling
            sale.total_cost_amount = total_cost
            sale.gross_profit = total_selling - total_cost

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('travel.sale') or _('New')
        return super().create(vals_list)

    def action_confirm(self):
        for sale in self:
            if sale.state != 'draft':
                raise UserError(_("Only draft sales can be confirmed."))
            if not sale.line_ids:
                raise UserError(_("You cannot confirm a sale without lines."))
            sale.state = 'confirmed'

    def action_in_progress(self):
        for sale in self:
            if sale.state != 'confirmed':
                raise UserError(_("Only confirmed sales can be marked as In Progress."))
            sale.state = 'in_progress'

    def action_complete(self):
        for sale in self:
            sale.state = 'completed'

    def action_cancel(self):
        for sale in self:
            if sale.state == 'completed':
                raise UserError(_("You cannot cancel a completed sale."))
            sale.state = 'cancelled'

    def action_draft(self):
        for sale in self:
            sale.state = 'draft'
