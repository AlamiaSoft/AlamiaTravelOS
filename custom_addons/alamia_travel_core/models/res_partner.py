from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Extends standard Odoo contact for Travel OS needs
    is_travel_customer = fields.Boolean("Is Travel Customer", default=False)
    is_travel_supplier = fields.Boolean("Is Travel Supplier", default=False)
    
    travel_customer_type = fields.Selection([
        ('individual', 'Individual'),
        ('corporate', 'Corporate'),
        ('agent', 'B2B Agent')
    ], string="Customer Type")
    
    travel_supplier_type = fields.Selection([
        ('airline', 'Airline'),
        ('hotel', 'Hotel'),
        ('consulate', 'Consulate/Embassy'),
        ('insurance', 'Insurance Company'),
        ('other', 'Other Vendor')
    ], string="Supplier Type")

    cnic_passport = fields.Char("CNIC / Passport Number")
    whatsapp_number = fields.Char("WhatsApp Number")
    
    # Sub-agent & Partner extensions
    is_travel_agent = fields.Boolean("Is Sub-Agent / Partner", default=False)
    agent_code = fields.Char("Agent Code")
    default_commission_rate = fields.Float("Default Commission %", default=0.0)

    total_agent_sales_count = fields.Integer(string="Total Sales", compute="_compute_agent_stats")
    total_agent_sales_amount = fields.Float(string="Total Sales Amount", compute="_compute_agent_stats")
    total_agent_commission_amount = fields.Float(string="Total Commission Earned", compute="_compute_agent_stats")

    def _compute_agent_stats(self):
        for partner in self:
            sale_lines = self.env['travel.sale.line'].search([('agent_id', '=', partner.id)])
            partner.total_agent_sales_count = len(sale_lines.mapped('sale_id'))
            partner.total_agent_sales_amount = sum(sale_lines.mapped('selling_amount'))
            partner.total_agent_commission_amount = sum(sale_lines.mapped('commission_amount'))


