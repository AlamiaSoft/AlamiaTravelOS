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
    
    # Optional branch context (if multi-branch is setup)
    # branch_id = fields.Many2one('res.branch', string="Branch")
