from odoo import api, fields, models

class ServiceCatalog(models.Model):
    _name = 'travel.service.catalog'
    _description = 'Travel Service Catalog'
    _order = 'sequence, name'

    name = fields.Char('Service Name', required=True)
    code = fields.Char('Code', required=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', default=10)
    description = fields.Text('Description')

    category = fields.Selection([
        ('visa', 'Visa Processing'),
        ('ticket', 'Flight Ticket'),
        ('hotel', 'Hotel Booking'),
        ('package', 'Package / Tour'),
        ('insurance', 'Travel Insurance'),
        ('appointment', 'Consulate Appointment'),
        ('other', 'Other Service')
    ], string='Service Category', default='other', required=True)

    list_price = fields.Float('Standard Selling Price', default=0.0)
    standard_cost = fields.Float('Standard Cost', default=0.0)
    target_margin = fields.Float('Target Profit Margin %', compute='_compute_target_margin')

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

    def _compute_target_margin(self):
        for rec in self:
            if rec.list_price > 0:
                rec.target_margin = ((rec.list_price - rec.standard_cost) / rec.list_price) * 100.0
            else:
                rec.target_margin = 0.0


class TravelServicePackage(models.Model):
    _name = 'travel.service.package'
    _description = 'Travel Service Package / Bundle'
    _order = 'name'

    name = fields.Char('Package Name', required=True)
    code = fields.Char('Package Code', required=True)
    active = fields.Boolean('Active', default=True)
    description = fields.Text('Package Description')
    
    line_ids = fields.One2many('travel.service.package.line', 'package_id', string='Package Services')
    total_selling_price = fields.Float('Total Selling Price', compute='_compute_package_totals', store=True)
    total_cost_price = fields.Float('Total Supplier Cost', compute='_compute_package_totals', store=True)
    expected_profit = fields.Float('Expected Profit', compute='_compute_package_totals', store=True)

    @api.depends('line_ids.selling_amount', 'line_ids.cost_amount')
    def _compute_package_totals(self):
        for pkg in self:
            total_sell = sum(line.selling_amount for line in pkg.line_ids)
            total_cost = sum(line.cost_amount for line in pkg.line_ids)
            pkg.total_selling_price = total_sell
            pkg.total_cost_price = total_cost
            pkg.expected_profit = total_sell - total_cost



class TravelServicePackageLine(models.Model):
    _name = 'travel.service.package.line'
    _description = 'Travel Service Package Line'

    package_id = fields.Many2one('travel.service.package', string='Package', required=True, ondelete='cascade')
    service_id = fields.Many2one('travel.service.catalog', string='Service', required=True)
    quantity = fields.Float('Quantity', default=1.0, required=True)
    unit_price = fields.Float('Unit Price', default=0.0)
    cost_price = fields.Float('Supplier Cost', default=0.0)
    selling_amount = fields.Float('Selling Amount', compute='_compute_line_totals', store=True)
    cost_amount = fields.Float('Cost Amount', compute='_compute_line_totals', store=True)

    @api.depends('quantity', 'unit_price', 'cost_price')
    def _compute_line_totals(self):
        for line in self:
            line.selling_amount = line.quantity * line.unit_price
            line.cost_amount = line.quantity * line.cost_price

    @api.onchange('service_id')
    def _onchange_service_id(self):
        if self.service_id:
            self.unit_price = self.service_id.list_price
            self.cost_price = self.service_id.standard_cost

