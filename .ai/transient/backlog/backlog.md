# Backlog — Pending Tasks

## Priority: High

- [ ] Execute Task-1 in Odoo MCP: inspect existing service categories and products, extract raw Excel labels from Kamal Express workbook
- [ ] Execute Task-2 in Odoo MCP: create missing canonical services/categories, verify no duplicates, produce verification report
- [ ] Populate `.ai/transient/sprint/01-next-state.md` after Task-1 completion
- [ ] Set up production VPS with Nginx + Let's Encrypt SSL for `travelos.yourcompany.com`

## Priority: Medium

- [ ] Populate remaining ADRs (ACP Server auth design, incremental migration pattern)
- [ ] Create `.ai/transient/handoffs/` session summaries
- [ ] Document Kamal Express Excel workbook structure in `docs/kamal-express/`
- [ ] Verify `scripts/backup.sh` cron job runs correctly on VPS
- [ ] Test Odoo chat WebSocket passthrough (port 8072) behind Nginx in production

## Priority: Low

- [ ] Update `.ai/permanent/architecture/01-system-architecture.md` with any new architectural discoveries
- [ ] Add more glossary terms as project terminology expands
- [ ] Document MCP server rate limiting thresholds and tuning
- [ ] Create `.ai/history/` timeline entries for sprint-by-sprint changes
- [ ] Write `.ai/lessons/` entries for debugging outcomes and failed experiments

## Future Considerations

- [ ] Evaluate Odoo 19 Community vs Enterprise feature gaps for travel use case
- [ ] Consider containerizing Nginx (currently host-level only) for full Docker Compose parity
- [ ] Evaluate switching to MariaDB if PostgreSQL compatibility issues arise
- [ ] Review Odoo proxy_mode implications for WebSocket support
- [ ] Document scaling considerations (multiple web containers behind load balancer)