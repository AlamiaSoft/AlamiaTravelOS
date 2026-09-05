# Repository Health — AlamiaTravelOS

## Architecture Drift Tracking

| Area | Status | Notes |
|------|--------|-------|
| Docker Compose dev/prod parity | ✅ In sync | Prod uses named volumes; dev uses bind mounts (intentional) |
| Custom addons structure | ✅ Healthy | 4 modules following Odoo naming conventions |
| MCP Server addon | ✅ Healthy | Controllers, models, tests all present (30+ test files) |
| Documentation coverage | 🟡 Partial | README complete; `.ai/` knowledge base now populated; migration guides present |
| Data migration runner | ⏳ Not started | Task-1/Task-2 defined but not executed in Odoo |

## Documentation Coverage Map

| Document | Exists? | Coverage |
|----------|---------|----------|
| `README.md` | ✅ | User quick start, deployment guide, security best practices |
| `.ai/README.md` | ✅ | Bootstrap read order + directory structure |
| `.ai/permanent/architecture/01-system-architecture.md` | ✅ | System layers, data flow, deployment patterns |
| `.ai/permanent/standards/01-coding-standards.md` | ✅ | Odoo/Python/YAML/Markdown conventions |
| `.ai/permanent/glossary/glossary.md` | ✅ | Project terminology single source of truth |
| `.ai/permanent/adr/` | 🟡 | index.md + ADR-001 present; more to add |
| `.ai/indexes/repository.md` | ✅ | Concept → code mappings |
| `.ai/indexes/dependency-map.md` | ✅ | Mermaid component/service/network graphs |
| `.ai/transient/sprint/00-current-state.md` | ✅ | Sprint 0 current state |
| `.ai/transient/backlog/backlog.md` | ✅ | Prioritized pending tasks |
| `.ai/transient/handoffs/session-1.md` | ✅ | Session 1 handoff |
| `.ai/history/sprint-0.md` | ✅ | Sprint 0 timeline |
| `.ai/lessons/lessons-2026-09-05.md` | ✅ | Debugging outcomes |
| `.ai/transient/repository-health.md` | ✅ | This file |
| `docs/kamal-express/data-import/task-1.md` | ✅ | Migration phase 1 |
| `docs/kamal-express/data-import/task-2.md` | ✅ | Migration phase 2 |
| `docs/kamal-express/users-roles-setup/spec.md` | ✅ | User/role setup spec |

## Missing Documentation

- [ ] `docs/kamal-express/` workbook schema documentation (columns, sheets)
- [ ] Explicit ADR for MCP Server auth design
- [ ] Production ops runbook (Portainer redeploy steps, volume backup/restore walkthrough)
- [ ] WebSocket troubleshooting guide for Odoo chat behind Nginx

## Current Drift Concerns

1. **Dev/prod compose divergence** — intentional (bind vs named volumes), but documented in ADR-001 to avoid future confusion
2. **`config/nginx/odoo.conf`** template exists but not validated for current domain
3. **Backup script** (`scripts/backup.sh`) exists but cron setup not yet verified on VPS

## Metrics

- **Knowledge base files**: 13 populated (was 0 at sprint start)
- **Test coverage (MCP addon)**: ~30 test files in `third_party_addons/mcp_server/tests/`
- **Custom addons**: 4 modules
- **Branches**: main (single branch workflow)