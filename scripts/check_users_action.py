# -*- coding: utf-8 -*-
import odoo
from odoo.modules.registry import Registry
from odoo.api import Environment

registry = Registry('alamiatravelos')
with registry.cursor() as cr:
    env = Environment(cr, odoo.SUPERUSER_ID, {})
    users = env['res.users'].search([])
    print("--- USERS ACTION_ID ---")
    for u in users:
        print(f"User: {u.name} ({u.login}) -> action_id: {u.action_id.name if u.action_id else 'NONE'}")
