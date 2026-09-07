# AlamiaTravelOS — MCP Server & AI Copilot Integration Guide

This guide explains how developers and administrators can connect AI assistants and Copilots (**GitHub Copilot**, **Claude Desktop**, **VS Code AI extensions**, **Antigravity**, or custom LLM agents) to **AlamiaTravelOS** using the Model Context Protocol (MCP).

---

## 1. Overview

The **MCP Server** (`third_party_addons/mcp_server`) exposes standardized JSON-RPC 2.0 endpoints on `/mcp`. It allows AI models to safely inspect, query, and interact with Odoo business logic, sales orders, customer ledgers, and activity cockpits using authorized API keys.

### Enabled Models & Capabilities
- **`travel.sale` & `travel.sale.line`**: Create, search, and inspect travel bookings and sale lines.
- **`res.partner`**: Access customer profiles, sub-agent accounts, and commission stats.
- **`travel.service.catalog`**: Query selling prices, costs, and package bundle details.
- **`account.move` & `account.payment`**: View invoices, payments, and outstanding balances.
- **`mail.activity`**: Schedule, complete, and reassign tasks and activities.

---

## 2. Generating an MCP API Key

### Option A: Automated Script (CLI / Container)
Run the setup script inside the Odoo web container:
```bash
docker exec alamiatravelos_web python3 /mnt/extra-addons/../scripts/setup_mcp.py
```
This generates an administrative API key named `mcp_admin_key` and outputs:
```text
MCP_API_KEY=a1b2c3d4e5f6...
```

### Option B: Odoo Web UI (No Command Line)
1. Log in to Odoo as Administrator (`admin`).
2. Click your user profile in the top-right corner -> **Preferences**.
3. Scroll down to **Account Security** -> **API Keys**.
4. Click **Generate API Key**, enter description `MCP Copilot Key`, and set scope to `mcp`.
5. Copy the generated secret key.

---

## 3. Configuring External AI Assistants

### A. Claude Desktop Configuration
Add the MCP server configuration to your `claude_desktop_config.json`:

- **Path on Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Path on macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "alamia-travel-os": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-fetch",
        "https://travels.alamiaconnect.com/mcp"
      ],
      "env": {
        "HTTP_HEADER_AUTHORIZATION": "Bearer YOUR_GENERATED_MCP_API_KEY"
      }
    }
  }
}
```

### B. VS Code / GitHub Copilot Configuration
Add the configuration to `.vscode/mcp.json` or your VS Code user `settings.json`:

```json
{
  "mcp.servers": {
    "AlamiaTravelOS": {
      "url": "https://travels.alamiaconnect.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_GENERATED_MCP_API_KEY"
      }
    }
  }
}
```

---

## 4. API Request Format (curl / HTTP)

You can also send direct JSON-RPC 2.0 requests to `/mcp`:

```bash
curl -X POST https://travels.alamiaconnect.com/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_GENERATED_MCP_API_KEY" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.call_tool",
    "params": {
      "name": "search_read",
      "arguments": {
        "model": "travel.sale",
        "domain": [["state", "=", "draft"]],
        "fields": ["name", "partner_id", "total_selling_amount"]
      }
    }
  }'
```

---

## 5. Example AI Prompts & Commands

Once connected, you can ask your AI Copilot questions like:

- **Sales**: *"Show me all pending draft sales created this month."*
- **Activities**: *"What activities are due today for Tayyab?"*
- **Customers**: *"Find customer contact details for Syed Kamal Ahmed."*
- **Services**: *"What is the selling price and cost of 14-Day Umrah Quad Package?"*
- **Task Scheduling**: *"Schedule a To-Do activity for Jawad on customer Ali Raza regarding payment clearance."*

---

## 6. Alamia AI Employee Runtime — Role-Based Skills & Fact Tools

The **Alamia AI Employee Runtime** transforms standard MCP API access into a domain-aware **AI Employee Platform**. It decouples generic model access from role-based business capabilities.

### 6.1 Role-Based Skills System & Manifests (`alamia_ai_registry.py`)
- **`SkillDefinition`**: Structured abstraction defining a business capability (`skill_id`, `name`, `objectives`, `required_tools`, `risk_level`, `allowed_roles`).
- **`RoleManifest`**: AI Employee profile mapping roles to permitted skills (`ceo_assistant`, `operations_assistant`, `sales_assistant`, `accounting_assistant`, `ticketing_assistant`).
- **`SkillRegistry`**: Centralized lookup resolving allowed skills and tool catalogs for active user sessions.

#### Implemented Skills Catalog
1. **`customer_360`**: Single-call 360° customer dossier (LTV, active bookings, unpaid balances, activities).
2. **`booking_360`**: Comprehensive booking status (`KE-XXXXX`), passenger passports, visa readiness, and supplier line allocations.
3. **`booking_readiness`**: Departure readiness analysis, missing passport/visa document alerts, and unconfirmed supplier allocations.
4. **`daily_briefing`**: Role-scoped morning work summary prioritizing overdues and operational tasks.
5. **`payment_followup`**: Receivables shortfall analysis and `mail.activity` proposal generation with chatter audit logs.
6. **`booking_profitability`**: Deterministic financial calculation of selling amounts, supplier costs, commissions, and margin %.
7. **`work_queue`**: Operational task filtering by urgency (`critical`, `attention`, `routine`).

### 6.2 Session Bootstrap
- **`get_employee_profile`**: First call in an AI session to bootstrap user identity, role profile, allowed skills, allowed tools, and session context before operational tools are exposed to the model.

### 6.3 Action Tools & Backend-Derived Security
- **`propose_action`**: Generates a validated `ActionProposal` payload (`action_id`, `idempotency_key`, `risk_level`, `requires_confirmation`).
- **`create_followup`**: Level 1 write tool creating `mail.activity` and posting an automated chatter audit log entry (`"Action executed via Alamia Travels AI by User X"`).
- **Backend-Derived Security**: Role permissions, risk levels, and confirmation policies are strictly derived and enforced by the backend (`ActionStateMachine`).


