from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class TravelSaleLine(models.Model):
    _name = 'travel.sale.line'
    _description = 'Travel Sale Line'
    _inherit = ['mail.thread']  # Enables per-line chatter tracking

    sale_id = fields.Many2one('travel.sale', string='Sale Reference', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(string='Sequence', default=10)

    service_id = fields.Many2one('travel.service.catalog', string='Service Category', required=True, tracking=True)
    description = fields.Char(string='Description', required=True)

    quantity = fields.Float(string='Quantity', default=1.0, required=True, digits='Product Unit of Measure', tracking=True)

    # Financial fields — tracked for full audit trail
    currency_id = fields.Many2one(related='sale_id.currency_id', store=True)
    unit_price = fields.Monetary(string='Unit Price', required=True, default=0.0, tracking=True)
    selling_amount = fields.Monetary(string='Selling Amount', compute='_compute_amounts', store=True)

    # Supplier info — tracked
    supplier_id = fields.Many2one('res.partner', string='Supplier', domain="[('is_travel_supplier', '=', True)]", tracking=True)
    cost_amount = fields.Monetary(string='Supplier Cost', default=0.0, tracking=True)

    # Gross profit
    gross_profit = fields.Monetary(string='Gross Profit', compute='_compute_amounts', store=True)

    @api.depends('quantity', 'unit_price', 'cost_amount')
    def _compute_amounts(self):
        for line in self:
            line.selling_amount = line.quantity * line.unit_price
            line.gross_profit = line.selling_amount - line.cost_amount

    @api.constrains('unit_price', 'cost_amount')
    def _check_positive_amounts(self):
        for line in self:
            if line.unit_price < 0.0:
                raise ValidationError(_("Unit price cannot be negative."))
            if line.cost_amount < 0.0:
                raise ValidationError(_("Supplier cost cannot be negative."))

    def write(self, vals):
        """
        Audit trail write-guard:
        Prevent silent financial mutations on completed or cancelled sales.
        Price/cost fields are locked once the sale is completed.
        """
        financial_fields = {'unit_price', 'cost_amount', 'quantity', 'selling_amount', 'supplier_id', 'service_id'}
        if financial_fields & set(vals.keys()):
            for line in self:
                if line.sale_id.state == 'completed':
                    raise UserError(_(
                        "Financial fields on sale line '%(desc)s' cannot be modified once the sale "
                        "is Completed. Use a credit note or cancellation workflow instead.",
                        desc=line.description
                    ))
                if line.sale_id.state == 'cancelled':
                    raise UserError(_(
                        "Cannot modify a cancelled sale line '%(desc)s'.",
                        desc=line.description
                    ))
        return super().write(vals)

    @api.onchange('service_id')
    def _onchange_service_id(self):
        if self.service_id and not self.description:
            self.description = self.service_id.name
