# Repository Index — AlamiaTravelOS

## High-Level Concepts → Source Code Mappings

| Concept | File(s) | Description |
|---------|---------|-------------|
| **Odoo 19 Docker Stack** | `docker-compose.yml`, `docker-compose.prod.yml` | Two-compose setup: dev vs production. Services: `web`, `db`. Named volumes for portability. |
| **Custom Addons** | `custom_addons/alamia_travel_core/`, `alamia_travel_sales/`, `alamia_travel_finance/`, `alamia_travel_reporting/` | In-house Odoo 19 modules. Provide travel-specific functionality: partner management, sales pipeline, finance tracking, dashboards. |
| **Third-Party Addons** | `third_party_addons/mcp_server/` | MCP Server with authentication (API keys, OAuth2), rate limiting, user context tools, model interaction utilities. |
| **MCP Protocol** | `third_party_addons/mcp_server/models/`, `controllers/`, `tools/` | External tool integration layer. Supports API key auth, OAuth2 flow, user context propagation, rate-limited model read/write. |
| **Data Migration** | `docs/kamal-express/data-import/task-1.md`, `task-2.md` | Incremental Kamal Express Excel → Odoo migration. Task 1: catalogue inspection/normalization. Task 2: service creation. Stop-and-verify pattern. |
| **Volume Management** | `docker-compose.prod.yml` (lines 66-80) | Named volumes: `odoo-config`, `custom-addons`, `third-party-addons`, `odoo-web-data`, `odoo-db-data`. Avoids bind-mount type mismatches on VPS. |
| **Management Scripts** | `scripts/manage.ps1`, `scripts/manage.sh` | Cross-platform Odoo lifecycle: up/down/restart/logs/build/scaffold/shell. Windows PowerShell & Linux/macOS compatible. |
| **Backup System** | `scripts/backup.sh` | PostgreSQL + filestore automated backup. Cron-scheduled at 2 AM. Creates compressed dumps, rotates logs. |
| **Nginx Reverse Proxy** | `config/nginx/odoo.conf` | Production SSL termination + WebSocket passthrough. Template shipped for host-level install via Certbot. |
| **Configuration** | `config/odoo.conf` | Odoo startup config: addons_path, limit_memory settings, proxy_mode=True, log_db, db_sslmode. |
| **Environment Config** | `.env`, `.env.example` | secrets: `DB_PASSWORD`, `ODOO_ADMIN_PASSWORD`, `DB_USER`, `DB_NAME`, `WEB_PORT`, `CHAT_PORT`, `DOMAIN`, `LETSENCRYPT_EMAIL`. Git-ignored in production. |
| **Architecture Decisions** | `docs/kamal-express/` | Guides for VPS provisioning, Kamal Express migration, user/role setup. |
| **Glossary** | `.ai/permanent/glossary/` (planned) | Single source of truth for project terminology (in progress). |
| **Sprint State** | `.ai/transient/sprint/00-current-state.md` (planned) | Current sprint focus, objectives, and delta summary between chats. |

## Directory Structure Map

```
AlamiaTravelOS/
├── .ai/                          # AI Knowledge Base (see .ai/README.md for read order)
│   ├── permanent/
│   │   ├── architecture/01-system-architecture.md   # System design intent
│   │   ├── standards/01-coding-standards.md         # Python/YAML conventions
│   │   ├── glossary/                                # Terminology (populated later)
│   │   └── adr/                                     # Architecture Decision Records
│   ├── indexes/
│   │   ├── repository.md                            # This file: concept→code mapping
│   │   └── dependency-map.md                        # Mermaid component graph
│   ├── history/                                     # Sprint-by-sprint timeline
│   ├── lessons/                                     # Debugging outcomes
│   ├── transient/
│   │   ├── sprint/00-current-state.md               # Current sprint focus
│   │   ├── backlog/                                 # Pending tasks
│   │   └── handoffs/                                # Session handoff summaries
│   └── README.md                                    # Bootstrap read order
├── config/                           # Runtime configuration
│   ├── odoo.conf                     # Odoo startup settings
│   └── nginx/                        # Nginx proxy template
├── custom_addons/                    # In-house Odoo modules
│   ├── alamiatravel_core/
│   ├── alamiatravel_sales/
│   ├── alamiatravel_finance/
│   └── alamiatravel_reporting/
├── third_party_addons/               # OCA/3rd-party modules
│   └── mcp_server/                   # MCP protocol + auth tools
├── docs/                             # Project documentation
│   ├── kamal-express/                # VPS deployment + migration guides
│   │   └── data-import/              # Task-1, task-2, etc.
│   └── README.md                     # User quick-start guide
├── docker-compose.yml                # Development stack (relative volumes)
├── docker-compose.prod.yml           # Production stack (named volumes)
├── Dockerfile                        # Custom Odoo 19 image build
├── .env                              # Local secrets (git-ignored)
├── .env.example                      # Env var template (committed)
├── .gitignore                        # Git rules (ignores .env, __pycache__, .pyc)
├── manage.ps1                        # Windows PowerShell management
├── manage.sh                         # Linux/macOS management helper
├── scripts/                          # Backup + automation scripts
│   ├── backup.sh
│   ├── manage.ps1
│   └── manage.sh
└── README.md                         # User documentation