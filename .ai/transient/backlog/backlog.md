# Backlog — Pending Tasks & Next Sprint Objectives

## Immediate Next Sprint Objectives (User Requested)

- [ ] **Default Login Landing Page**: Configure TravelOS Executive/Role Dashboard as default landing app after login (replacing default Discuss app).
- [ ] **Expenses Management Screens**: Dedicated views for Office Expenses, Categories, Payees, and Expense Approvals.
- [ ] **Services / Products / Subscriptions Management Screens**: Expanded catalog management for travel services, package subscriptions, and service pricing tiers.
- [ ] **Sub-Agents & Partners Management Screens**: Comprehensive Partner & Sub-Agent views, commission tracking, and partner settlement ledgers.
- [ ] **Advanced Accounting & Finance Features**: Aged Receivables/Payables, Financial Statements, Journal Entries, and Cash/Bank Position tracking.

---

## Priority: Medium

- [ ] Verify production deployment on VPS (`travels.alamiaconnect.com`) via Portainer.
- [ ] Test Odoo chat WebSocket passthrough (port 8072) behind Nginx/Cloudflare Tunnel in production.
- [ ] Document MCP server rate limiting thresholds and tuning.
- [ ] Verify `scripts/backup.sh` cron job runs correctly on VPS.

---

## Priority: Low

- [ ] Populate remaining ADRs for architectural decisions.
- [ ] Document scaling considerations (multiple web containers behind load balancer).