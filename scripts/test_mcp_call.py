import subprocess
import urllib.request
import json

gen_code = """
admin = env['res.users'].browse(2)
mcp_group = env.ref('mcp_server.group_mcp_admin', raise_if_not_found=False) or env.ref('mcp_server.group_mcp_user', raise_if_not_found=False)
if mcp_group and mcp_group.id not in admin.group_ids.ids:
    admin.write({'group_ids': [(4, mcp_group.id)]})

# Delete existing mcp keys for admin
env['res.users.apikeys'].search([('name', '=', 'mcp_script_key')]).unlink()

admin_env = env(user=admin)
key = admin_env['res.users.apikeys']._generate(scope='mcp', name='mcp_script_key', expiration_date=False)
print("SAVED_KEY:" + key)
"""

p = subprocess.Popen(['docker', 'compose', 'exec', '-T', 'web', 'odoo', 'shell', '-d', 'alamiatravelos', '--no-http'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
out, _ = p.communicate(gen_code.encode())

api_key = None
for line in out.decode('utf-8').splitlines():
    if "SAVED_KEY:" in line:
        api_key = line.split("SAVED_KEY:")[1].strip()

print(f"Active MCP Key: {api_key}")

if api_key:
    url = "http://localhost:8069/mcp?db=alamiatravelos"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 1. Initialize
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2025-11-25"}
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
    res = json.loads(urllib.request.urlopen(req).read().decode())
    print("\n--- MCP Initialize Response ---")
    print(json.dumps(res, indent=2))

    # 2. List Tools
    payload_tools = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    req_tools = urllib.request.Request(url, data=json.dumps(payload_tools).encode('utf-8'), headers=headers)
    res_tools = json.loads(urllib.request.urlopen(req_tools).read().decode())
    print("\n--- MCP Available Tools ---")
    tools = res_tools.get("result", {}).get("tools", [])
    print([t["name"] for t in tools])

    # 3. Call Tool: search_read on travel.sale
    payload_call = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "search_read",
            "arguments": {
                "model": "travel.sale",
                "domain": [],
                "fields": ["id", "name", "total_selling_amount", "state"],
                "limit": 3
            }
        }
    }
    req_call = urllib.request.Request(url, data=json.dumps(payload_call).encode('utf-8'), headers=headers)
    res_call = json.loads(urllib.request.urlopen(req_call).read().decode())
    print("\n--- MCP Call Result (search_read on travel.sale) ---")
    print(json.dumps(res_call, indent=2))
