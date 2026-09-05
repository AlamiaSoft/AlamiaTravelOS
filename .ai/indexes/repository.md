# Repository Index — AlamiaTravelOS

## High-Level Concepts → Source Code Mappings

| Concept | File(s) | Description |
|---------|---------|-------------|
| **Odoo 19 Docker Stack** | `docker-compose.yml`, `docker-compose.prod.yml` | Two-compose setup: dev (`alamiatravelos_web`) vs production (`alamiatravelos_web_prod`). Services: `web`, `db`. Container healthchecks configured on postgres. |
| **Core Master Data** | `custom_addons/alamia_travel_core/` | Service catalog (`travel.service.catalog`), customer/supplier partner flags, top-level menus, and 5 role groups (`travel_role_ceo`, etc.). |
| **Sales Engine** | `custom_addons/alamia_travel_sales/` | `travel.sale` (`KE-YYYY-XXXXX` sequence, lifecycle `draft`→`confirmed`→`in_progress`→`completed`), `travel.sale.line` with audit trail & write-guard. |
| **Finance Integration** | `custom_addons/alamia_travel_finance/` | Extends `account.move` with `travel_sale_id`. Invoice & bill creation buttons on sale. `payment_status` compute logic. |
| **Dashboards & Reporting** | `custom_addons/alamia_travel_reporting/` | `travel.dashboard` AbstractModel backend service + OWL component client action (`travel_dashboard.js`, `travel_dashboard.xml`, SCSS). |
| **User Provisioning & Roles** | `custom_addons/alamia_travel_core/data/users_data.xml`, `security/security.xml` | Provisioned users (Kamal, Jawad, Ali, Tayyab, Zeeshan). Role-based security matrix & implied permissions. |
| **Third-Party Addons** | `third_party_addons/mcp_server/` | MCP Server integration with API key auth (`setup_mcp.py`), JSON-RPC 2.0 endpoints on `/mcp`. |
| **Automated Tests** | `custom_addons/alamia_travel_finance/tests/test_golden_scenarios.py`, `custom_addons/alamia_travel_reporting/tests/test_users_roles_and_dashboards.py` | 5 Golden Financial Scenarios + 18 User/Role/Dashboard security tests (23 total tests). |
| **Management Scripts** | `scripts/setup_mcp.py` | Automated MCP server configuration script. |
| **Dockerfile** | `Dockerfile` | Custom Odoo 19 image with Python dependencies (`phonenumbers`, `xlsxwriter`, `authlib`, etc.) and copied custom addons. |
| **Environment Config** | `.env`, `.env.example`, `config/odoo.conf` | Runtime secrets & Odoo configuration (`proxy_mode=True`, `workers`, memory limits). |

## Directory Structure Map

```
AlamiaTravelOS/
├── .ai/                                  # AI Knowledge Base (see .ai/README.md for read order)
│   ├── permanent/
│   │   ├── architecture/01-system-architecture.md   # System design intent
│   │   ├── standards/01-coding-standards.md         # Python/YAML conventions
│   │   ├── glossary/                                # Terminology
│   │   └── adr/                                     # Architecture Decision Records
│   ├── indexes/
│   │   ├── repository.md                            # Concept → code mapping
│   │   └── dependency-map.md                        # Mermaid component graph
│   ├── history/                                     # Sprint-by-sprint timeline
│   ├── lessons/                                     # Debugging outcomes & lessons learned
│   └── transient/
│       ├── sprint/00-current-state.md               # Current sprint focus
│       ├── backlog/                                 # Pending tasks
│       └── handoffs/                                # Session handoff summaries
├── config/                               # Runtime configuration
│   ├── odoo.conf                         # Odoo startup settings
│   └── nginx/                            # Nginx proxy template
├── custom_addons/                        # In-house Odoo modules
│   ├── alamiatravel_core/                # Master data & security groups
│   ├── alamiatravel_sales/               # Sales pipeline & sale lines
│   ├── alamiatravel_finance/             # Accounting integration & golden scenario tests
│   └── alamiatravel_reporting/           # Executive & role dashboards + permission tests
├── third_party_addons/                   # OCA/3rd-party modules
│   └── mcp_server/                       # MCP protocol + auth tools
├── docs/                                 # Project documentation
│   └── kamal-express/                    # Migration & user specs
├── docker-compose.yml                    # Development stack
├── docker-compose.prod.yml               # Production stack (Portainer / VPS)
├── Dockerfile                            # Custom Odoo 19 image build
├── .env                                  # Local secrets (git-ignored)
├── .env.example                          # Env var template
└── scripts/                              # Setup & automation scripts
    └── setup_mcp.py
```