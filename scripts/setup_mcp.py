import os
import sys

# Add odoo to path
import odoo
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry

# Initialize environment
odoo.tools.config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', 'alamiatravelos'])
reg = Registry('alamiatravelos')

with reg.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    admin = env['res.users'].browse(2)
    
    existing_key = env['res.users.apikeys'].search([('name', '=', 'mcp_admin_key'), ('user_id', '=', admin.id)])
    if not existing_key:
        admin_env = env(user=admin)
        key = admin_env['res.users.apikeys']._generate(scope='mcp', name='mcp_admin_key', expiration_date=False)
        print(f"MCP_API_KEY={key}")
    else:
        print("MCP_API_KEY=ALREADY_GENERATED")
    
    # Enable models
    models_to_enable = ['travel.service.catalog', 'res.partner', 'account.move', 'account.payment', 'travel.sale', 'travel.sale.line']
    for model_name in models_to_enable:
        model = env['ir.model'].search([('model', '=', model_name)])
        if model:
            existing = env['mcp.enabled.model'].search([('model_id', '=', model.id)])
            if not existing:
                env['mcp.enabled.model'].create({
                    'model_id': model.id,
                    'allow_read': True,
                    'allow_create': True,
                    'allow_write': True,
                    'allow_unlink': True
                })
                print(f"Enabled model: {model_name}")

    env['ir.config_parameter'].sudo().set_param('mcp_server.enabled', 'True')
    env.registry.clear_cache()
    print("MCP Server Enabled Globally!")

