# Glossary — AlamiaTravelOS

## Project Terminology (Single Source of Truth)

### General

| Term | Definition |
|------|------------|
| **AlamiaTravelOS** | Dockerized Odoo 19.0 Community Edition deployment setup optimized for local development and VPS production deployment (Hetzner/Oracle Cloud). |
| **MCP Server** | Model Context Protocol integration layer (`third_party_addons/mcp_server`) providing authentication (API keys, OAuth2), rate limiting, and user context tools for external system integration. |
| **Kamal Express** | Historical data export brand; Excel workbook containing legacy service/order data being migrated into Odoo via incremental task pipeline. |
| **Data Migration** | Incremental Odoo record import process defined in `docs/kamal-express/data-import/`. Stop-and-verify pattern after each batch. |
| **Named Volumes** | Docker Compose volume type where Docker manages volume lifecycle and location; used in `docker-compose.prod.yml` for production portability. |
| **Bind Mount** | Docker volume type mapping host filesystem path directly into container; used in `docker-compose.yml` for local dev convenience. |
| **Portainer** | Docker container management UI; used for "Add New Stack" VPS deployment of `docker-compose.prod.yml`. |

### Odoo-Specific

| Term | Definition |
|------|------------|
| **Odoo 19** | Open-source ERP/CRM platform (Community Edition) version 19.0; base platform for AlamiaTravelOS. |
| **Odoo Container** | Docker container running the Odoo application server (`web` service in compose). |
| **Odoo MCP** | The MCP Server integration within Odoo, enabling external tool interaction via JSON-RPC, API keys, and model context. |
| **Custom Addon** | In-house Odoo module under `custom_addons/` (e.g., `alamia_travel_core`, `alamia_travel_sales`). |
| **Third-Party Addon** | Community or OCA module under `third_party_addons/` (e.g., `mcp_server`, reporting tools). |
| **Proxymode** | Odoo setting (`proxy_mode = True` in `odoo.conf`) that accurately handles client IP and SSL headers when behind a reverse proxy (Nginx). |
| **Filestore** | Odoo attachment storage system; files stored in Docker volumes under `data/` directory. |
| **Healthcheck** | Docker Compose `healthcheck` directive (e.g., PostgreSQL `pg_isready`) to verify service readiness before dependent services start. |

### Docker & Infrastructure

| Term | Definition |
|------|------------|
| **Compose File** | `docker-compose.yml` (development) or `docker-compose.prod.yml` (production); defines services, networks, volumes. |
| **Named Volume** | Volume defined in `volumes:` section at bottom of compose file; Docker manages lifecycle; used in production for portability. |
| **Bind Mount** | Volume mapping host absolute/relative path into container; used in development for easy host-side editing. |
| **VPS** | Virtual Private Server (Hetzner Cloud / Oracle Cloud) where production stack is deployed. |
| **Portainer** | Web UI for managing Docker stacks/compose on VPS; entry point for `docker compose up` deployment. |
| **Docker Network** | `odoo-network` (bridge) — internal network connecting `web` and `db` services; enables inter-container communication. |
| **Environment Variable** | `${VAR:-default}` pattern for configurable defaults; set via Portainer UI, `.env` file, or `docker-compose.override`. |
| **Dockerfile** | Custom image build script (`Dockerfile`) extending `odoo:19.0` with enterprise Python dependencies pre-installed. |
| **Reverse Proxy** | Host-level Nginx (not inside Docker) terminating SSL, handling Certbot, and forwarding to Odoo internal port. |
| **Let's Encrypt** | Free SSL certificate authority; used with host-level Nginx for `travelos.yourcompany.com` domain. |

### Migration & Tasks

| Term | Definition |
|------|------------|
| **Task-1** | First phase of Kamal Express data migration: inspect existing Odoo models, extract & normalize raw Excel labels into canonical service catalogue. |
| **Task-2** | Second phase: create missing service categories/services in Odoo based on Task-1 planning; verify no duplicates; produce report. |
| **Raw Excel Label** | Original text string from Kamal Express workbook; mapped to canonical Category → Service in migration. |
| **Canonical Service** | Normalized service name in Odoo (e.g., "Visit Visa" under "Visa" category), merging multiple raw labels. |
| **Category** | Odoo `crm.service.category` or custom model grouping related services (e.g., "Visa", "Hotel", "Apostille"). |
| **Verification Report** | Post-creation documentation showing: Created categories/services, Reused existing records, Skipped duplicates, Needs review (ambiguous mappings). |
| **Incremental Migration** | Approach where data is imported in small batches with verification after each, rather than one-shot bulk import. |

### File Locations

| Term | File Path |
|------|-----------|
| **System Architecture** | `.ai/permanent/architecture/01-system-architecture.md` |
| **Coding Standards** | `.ai/permanent/standards/01-coding-standards.md` |
| **Repository Index** | `.ai/indexes/repository.md` |
| **Current Sprint State** | `.ai/transient/sprint/00-current-state.md` |
| **Architecture ADRs** | `.ai/permanent/adr/` |
| **Data Import Guides** | `docs/kamal-express/data-import/task-1.md`, `task-2.md` |
| **Production Compose** | `docker-compose.prod.yml` |
| **Development Compose** | `docker-compose.yml` |
| **Odoo Config** | `config/odoo.conf` |
| **Nginx Template** | `config/nginx/odoo.conf` |
| **Management Scripts** | `scripts/manage.ps1`, `scripts/manage.sh` |
| **Backup Script** | `scripts/backup.sh` |
| **MCP Server** | `third_party_addons/mcp_server/` |

### Abbreviations

| Abbreviation | Full Form |
|--------------|-----------|
| **API** | Application Programming Interface |
| **CRUD** | Create, Read, Update, Delete |
| **DDOS** | Distributed Denial of Service (not typically used here, included for completeness) |
| **GUI** | Graphical User Interface |
| **IP** | Internet Protocol |
| **ML** | Machine Learning (not typically used here) |
| **OEM** | Original Equipment Manufacturer (not applicable) |
| **OS** | Operating System |
| **PR** | Pull Request (git workflow) |
| **RPC** | Remote Procedure Call (Odoo JSON-RPC) |
| **SQL** | Structured Query Language |
| **SSL** | Secure Sockets Layer |
| **VPS** | Virtual Private Server |