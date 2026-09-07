# -*- coding: utf-8 -*-
import odoo
from odoo.modules.registry import Registry
from odoo.api import Environment

registry = Registry('alamiatravelos')
with registry.cursor() as cr:
    env = Environment(cr, odoo.SUPERUSER_ID, {})
    v2 = env.ref('base.res_partner_kanban_view')
    res2 = env['res.partner'].get_views([(v2.id, 'kanban')])
    print('BASE KANBAN ARCH:')
    print(res2['views']['kanban']['arch'])
