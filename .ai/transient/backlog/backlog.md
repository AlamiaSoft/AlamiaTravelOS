# Backlog — Pending Tasks & Next Phase Objectives

## Completed Core Phase 2 Objectives

- [x] **Default Login Landing Page**: Configured TravelOS Executive/Role Dashboard as default landing app after login.
- [x] **Expenses Management Screens**: Created `travel.expense.category` and `travel.expense` views under `Travel OS -> Expenses`.
- [x] **Services & Package Bundles**: Extended `travel.service.catalog` with selling prices, costs, margin %, and `travel.service.package`.
- [x] **Sub-Agents & Partners Management**: Partner extension with `is_travel_agent`, `agent_code`, default commission rate %, and live sales/commission stats under `Travel OS -> Operations -> Sub-Agents & Partners`.
- [x] **Role-Based Navigation Menu Tailoring**: Enforced menu access security matrix across Configuration, Finance, Reporting, and Operations.
- [x] **Global Task / To-Do Scheduling Shortcut**: 1-click popup wizard (`travel.schedule.activity.wizard`) accessible via top navbar and dashboard header.
- [x] **Financial Data Security Scoping**: Executive financial metrics (revenue, profit margins %, net income) restricted to `ceo` and `admin` roles.
- [x] **OCA Financial Reports Integration**: Integrated official `account_financial_report` suite under `Travel OS -> Finance -> Accounting Reports` (Balance Sheet, P&L, Trial Balance, General Ledger, Partner Ledgers).

---

## Pending Items & Next Phase Objectives

### 1. VPS Production UAT & Verification
- [ ] **VPS Portainer Redeploy Verification**: Confirm pull on `travels.alamiaconnect.com` renders new menu items, task wizard, and financial reports.
- [ ] **Live Chat WebSocket Passthrough (Port 8072)**: Verify bus notifications over Cloudflare Tunnel in production.
- [ ] **Automated Backup Cron (`scripts/backup.sh`)**: Confirm daily PostgreSQL & Filestore backups execute cleanly on VPS.

### 2. Operational Enhancements (Phase 3 Considerations)
- [ ] **Customer WhatsApp / SMS Reminders**: Automated payment and booking status alerts sent to customers.
- [ ] **Passport & Visa Expiry Alerts**: Automated activity generation when customer travel documents approach expiry.
- [ ] **Sub-Agent Portal Ledger**: Dedicated portal view for sub-agents to view booking statuses and commission balances.