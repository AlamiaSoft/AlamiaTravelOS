# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _default_action_id(self):
        try:
            action = self.env.ref('alamia_travel_reporting.action_travel_dashboard_main', raise_if_not_found=False)
            return action.id if action else False
        except Exception:
            return False

    action_id = fields.Many2one(default=_default_action_id)
