# System Architecture — AlamiaTravelOS

## Overview
AlamiaTravelOS is a **Dockerized Odoo 19.0 Community Edition** deployment optimized for:
- **Local development** on Windows/macOS/Linux via Docker Desktop
- **Production deployment** on VPS (Hetzner Cloud / Oracle Cloud) with self-managed Nginx reverse proxy + Let's Encrypt SSL

## Architecture Layers

### 1. Infrastructure Layer
- **Docker Engine** + **Docker Compose Plugin** (v2)
- **PostgreSQL 17** container for relational data storage
- **Odoo 19.0** custom image (`Dockerfile`) with enterprise Python dependencies pre-installed
- **Host-level Nginx** (production only) for SSL termination and WebSocket passthrough

### 2. Application Layer
- **Odoo Services**:
  - `web` — Odoo application server (default port 8069, chat on 8072)
  - `db` — PostgreSQL database server with health checks
- **Custom Addons** (`custom_addons/`):
  - `alamia_travel_core` — Base travel module (partners, catalog, etc.)
  - `alamia_travel_sales` — Sales pipeline & opportunity tracking
  - `alamia_travel_finance` — Accounting, invoices, goldenscenarios
  - `alamia_travel_reporting` — Dashboards, travel dashboards, user/role setups
- **Third-Party Addons** (`third_party_addons/`):
  - **MCP Server** (Model Context Protocol) — Authentication, API keys, OAuth2, rate limiting, user context tools
  - OCA community modules for advanced reporting, UI extensions

### 3. Data Layer
- **Filestore** — Odoo attachments stored in Docker volumes
- **PostgreSQL data** — Persisted via named volumes (`odoo-db-data`)
- **Custom config** — `config/odoo.conf` for proxy mode, addons paths, limits

### 4. Integration Layer
- **MCP Protocol** — External tool integration (API keys, OAuth, model context)
- **Kamal Express Excel migration** — Historical data import task pipeline (task-1.md → task-2.md)
- **Backup system** — `scripts/backup.sh` (PostgreSQL + filestore cron job)
- **Management scripts** — `scripts/manage.ps1` (Windows) / `manage.sh` (Linux/macOS)

### 5. Deployment Patterns

| Environment | Compose File | Key Differences |
|-------------|-------------|-----------------|
| **Local Dev** | `docker-compose.yml` | Relative path volumes (`./config/...`), dev command `["--dev=reload,xml"]`, admin password from `.env` |
| **Production VPS** | `docker-compose.prod.yml` | Named volumes (portability), `restart: always`, env vars with defaults, Portainer-ready |
| **Production w/ SSL** | `docker-compose.prod.yml` + Host Nginx | Ports 80/443 mapped to host, Certbot SSL, Nginx config in `config/nginx/` |

### 6. Key Design Decisions
- **Named volumes** in production compose (avoids bind-mount type mismatches on VPS/Portainer)
- **Environment variable defaults** with `${VAR:-default}` pattern for portability
- **MCP Server** as 3rd-party addon for external tool authentication (API keys, OAuth scopes)
- **Incremental data migration** via task docs (`docs/kamal-express/data-import/`) — stop-and-verify after each batch
- **No accounting modifications** in initial migration phases (per task-1.md rules)
- **Proxy mode = True** in `odoo.conf` for accurate client IP & SSL header handling behind Nginx

### 7. Data Flow
1. User access → Host Nginx (prod) or Direct Docker (dev) → Odoo Web Container
2. Odoo → PostgreSQL (internal Docker network `odoo-network`)
3. Odoo Addons → Custom filestore volumes
4. External tools → MCP Server (API key auth) → Odoo RPC/JSON-RPC
5. Data exports → `scripts/backup.sh` → Cron → Secure storage

### 8. Security Considerations
- `ODOO_ADMIN_PASSWORD` stored in `.env` (git-ignored), never committed
- PostgreSQL port 5432 **not** exposed publicly; internal network only
- Rate limiting via MCP server (`rate_limiting.py`) for API protection
- Strong passwords enforced for `DB_PASSWORD` and `ODOO_ADMIN_PASSWORD`
- `limit_memory_hard`/`soft` in `odoo.conf` to prevent container OOM