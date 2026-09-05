from odoo import fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    travel_sale_id = fields.Many2one('travel.sale', string='Travel Sale Ref', readonly=True, copy=False)
