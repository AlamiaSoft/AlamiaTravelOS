from odoo import api, fields, models, _

class TravelPartnerSettlement(models.Model):
    _name = 'travel.partner.settlement'
    _description = 'Travel Partner Settlement & Capital Transaction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True, tracking=True)

    partner_id = fields.Many2one('res.partner', string='Partner / Shareholder', required=True, tracking=True)

    settlement_type = fields.Selection([
        ('capital_advance', 'Capital Advance'),
        ('partner_drawing', 'Partner Drawing'),
        ('receipt', 'Receipt / Installment'),
        ('profit_distribution', 'Profit Distribution'),
        ('settlement', 'Settlement'),
        ('other', 'Other')
    ], string='Transaction Type', required=True, default='settlement', tracking=True)

    amount = fields.Monetary(string='Amount', required=True, default=0.0, tracking=True)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', store=True)

    notes = fields.Text(string='Notes / Reference', tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='posted', required=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('travel.partner.settlement') or _('New')
        return super().create(vals_list)
