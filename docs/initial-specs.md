# Alamia Travel OS

## Phase 1 — Operations & Financial Control

**Product:** Alamia Travel OS
**Initial Tenant:** Kamal Express
**Platform:** Odoo Community
**Deployment:** Local Docker during development
**Future:** Multi-tenant / reusable travel-industry product
**Phase:** 1 — Operations & Financial Control
**Status:** Implementation specification

---

# 1. Executive Objective

Kamal Express urgently needs a reliable system where staff can enter sales and operational transactions and management can immediately understand the company's financial position.

The current Jotform-based process is useful as an intake mechanism but is insufficient as the system of record because it does not provide a complete operational/accounting model.

Phase 1 must therefore establish:

1. Customer management
2. Sales/transaction entry
3. Receipts/payments
4. Supplier/vendor costs
5. Customer receivables
6. Supplier payables
7. Revenue/cost/profit visibility
8. Cash/bank visibility
9. Management reporting
10. Auditability
11. Correct Odoo accounting integration
12. A foundation for future Travel OS modules

The Phase-1 system must be usable by a normal travel-agency accountant/operator without requiring developers to manually correct transactions.

---

# 2. Critical Product Principle

## Odoo is the financial source of truth.

Do NOT create a second accounting engine inside Travel OS.

Travel OS provides travel-specific operational entities and workflows.

Odoo Accounting provides:

* Chart of Accounts
* Customers
* Vendors
* Invoices
* Bills
* Payments
* Receivables
* Payables
* Journal Entries
* Bank/Cash accounts
* Reconciliation
* Accounting reports

Travel OS must integrate with these mechanisms rather than maintaining a parallel ledger.

---

# 3. Phase-1 Scope

## IN SCOPE

### Core

* Company
* Branch
* Users
* Roles
* Customers
* Suppliers
* Services
* Sales
* Sale lines
* Customer payments
* Supplier costs
* Supplier payments
* Documents/attachments
* Transaction status
* Audit trail

### Financial

* Customer receivables
* Supplier payables
* Revenue
* Cost
* Gross profit
* Cash
* Bank
* Payment methods
* Customer balances
* Supplier balances

### Reporting

* Sales dashboard
* Collections dashboard
* Receivables
* Payables
* Gross profit
* Sales by service
* Sales by salesperson
* Sales by branch
* Customer statement
* Supplier statement
* Daily/monthly summaries

### Travel service categories

Initial configurable services:

* Ticket
* Visa
* Hotel Booking
* Insurance
* Apostille
* Case Preparation
* Umrah
* Hajj
* Appointment
* Other

These must be configuration/data, NOT hard-coded application logic.

---

# 4. Explicitly OUT OF SCOPE for Phase 1

Do NOT implement these yet unless required for a Phase-1 dependency:

* GDS integration
* Airline API integration
* Automatic ticket issuance
* Visa portal automation
* Appointment slot automation
* Hajj group management
* Umrah group management
* Hotel inventory integration
* WhatsApp AI
* AI assistants
* Customer-facing portal
* SaaS billing
* Advanced multi-tenant control plane
* Complex commission engine
* Advanced CRM automation
* Marketing automation

The architecture must allow these later.

Do not allow future requirements to bloat Phase 1.

---

# 5. Target User Roles

Initial roles:

## Administrator

Full system access.

## Manager

* View all operations
* View financial dashboards
* View reports
* Approve sensitive operations
* Cannot silently alter accounting history

## Sales Staff

* Create customers
* Create sales
* View own transactions
* Record collections where permitted
* Cannot modify finalized accounting records

## Accountant

* View financial transactions
* Invoices
* Bills
* Payments
* Customer balances
* Supplier balances
* Reconciliation
* Reports

## Operations Staff

* View/create operational information
* Manage assigned transactions
* Upload documents
* Update workflow statuses

Permissions must be enforced server-side, not merely hidden in UI.

---

# 6. Domain Model

The Phase-1 conceptual model is:

```text
Company
  │
  ├── Branch
  │
  ├── Users
  │
  ├── Customers
  │      │
  │      └── Sales
  │             │
  │             ├── Sale Lines
  │             ├── Payments
  │             ├── Supplier Costs
  │             └── Documents
  │
  └── Suppliers
         │
         ├── Supplier Costs
         └── Supplier Payments
```

---

# 7. Customer

Customer fields:

```text
Customer
├── ID
├── Name
├── Customer Type
├── Phone
├── WhatsApp
├── Email
├── CNIC/Passport reference
├── Address
├── City
├── Country
├── Branch
├── Assigned salesperson
├── Notes
├── Documents
├── Sales
├── Payments
└── Balance
```

Use Odoo's existing partner/customer infrastructure wherever possible.

Do not unnecessarily duplicate `res.partner`.

---

# 8. Supplier

Supplier fields:

```text
Supplier
├── ID
├── Name
├── Supplier Type
├── Phone
├── Email
├── Country
├── Branch
├── Payment Terms
├── Notes
├── Costs
├── Bills
├── Payments
└── Balance
```

Use Odoo vendor infrastructure wherever possible.

---

# 9. Service Catalog

Services must be configurable.

Initial records:

```text
TICKET
VISA
HOTEL
INSURANCE
APOSTILLE
CASE_PREPARATION
UMRAH
HAJJ
APPOINTMENT
OTHER
```

Each service should support:

```text
Name
Code
Active
Revenue Account
Cost Account
Default taxes if applicable
Description
```

Do not encode service behavior with hard-coded `if service == "ticket"` logic.

---

# 10. Sales Transaction

A Sale is the primary operational transaction.

Concept:

```text
Sale
├── Reference
├── Date
├── Customer
├── Branch
├── Salesperson
├── Service
├── Supplier
├── Description
├── External Reference
├── Sale Lines
├── Selling Total
├── Cost Total
├── Gross Profit
├── Amount Paid
├── Amount Outstanding
├── Payment Status
├── Operational Status
├── Accounting Status
└── Documents
```

---

# 11. Sale Lines

Do not assume every future sale has one amount.

Support multiple lines.

Example:

```text
Sale #KE-000123

Customer: Ahmed Khan

Lines:

1. Airline Ticket       120,000
2. Baggage                8,000
3. Service Fee            5,000

Selling Total           133,000
```

Each line should support:

```text
Description
Service
Quantity
Unit Price
Selling Amount
Supplier
Supplier Cost
Cost Amount
Profit
```

Phase 1 may expose a simplified UI, but the underlying model must support multiple lines.

---

# 12. Financial Calculation Rules

These calculations must be deterministic.

## Selling Total

```text
SUM(all sale line selling amounts)
```

## Cost Total

```text
SUM(all sale line cost amounts)
```

## Gross Profit

```text
Selling Total - Cost Total
```

## Amount Paid

```text
SUM(valid payments allocated to sale)
```

## Outstanding

```text
Selling Total - Amount Paid
```

Never allow users to manually type the calculated outstanding amount.

Never trust client-side calculations.

The server must calculate and validate these values.

---

# 13. Payment Model

Payments are first-class transactions.

```text
Payment
├── Reference
├── Date
├── Customer
├── Sale
├── Amount
├── Payment Method
├── Financial Account
├── Collector
├── Reference Number
├── Notes
└── Accounting Entry
```

Initial payment methods:

```text
Cash
Bank Transfer
Card
Easypaisa
JazzCash
Cheque
Other
```

Financial account must identify where money actually went.

Example:

```text
Cash
→ Cash Account

Bank Transfer
→ HBL Bank

Bank Transfer
→ Meezan Bank

Easypaisa
→ Easypaisa Account
```

Do not merely store `"Bank"` as text.

---

# 14. Partial Payments

Must be supported.

Example:

```text
Sale = 150,000

Payment 1 = 50,000
Payment 2 = 30,000
Payment 3 = 20,000

Total Paid = 100,000
Outstanding = 50,000
```

Payment status:

```text
UNPAID
PARTIALLY_PAID
PAID
OVERPAID
```

Overpayment must be detected and handled explicitly.

Do not silently produce negative receivables.

---

# 15. Supplier Cost

Supplier cost must be separate from customer selling price.

Example:

```text
Customer Price = 150,000
Supplier Cost  = 120,000

Gross Profit = 30,000
```

Supplier cost should eventually map to:

* Vendor bill
* Payable
* Expense/cost account

depending on the accounting design.

Do not simply store vendor cost as an informational number.

---

# 16. Supplier Payments

Support:

```text
Supplier Bill
      ↓
Amount Due
      ↓
Supplier Payment
      ↓
Remaining Payable
```

Partial supplier payments must be supported.

---

# 17. Accounting Integration

Accounting integration must be tested, not assumed.

At minimum verify:

```text
Customer Sale
    ↓
Revenue
    ↓
Accounts Receivable

Customer Payment
    ↓
Receivable decreases
    ↓
Cash/Bank increases

Supplier Cost/Bill
    ↓
Expense/Cost
    ↓
Accounts Payable

Supplier Payment
    ↓
Payable decreases
    ↓
Cash/Bank decreases
```

Every accounting transaction must be traceable back to the originating operational transaction.

---

# 18. Transaction Lifecycle

Sales:

```text
DRAFT
  ↓
CONFIRMED
  ↓
IN_PROGRESS
  ↓
COMPLETED
```

Cancellation:

```text
DRAFT/CONFIRMED/IN_PROGRESS
          ↓
       CANCELLED
```

Accounting state must be independent:

```text
NOT_POSTED
POSTED
REVERSED
```

Do not confuse operational status with accounting status.

---

# 19. Immutability / Corrections

Once a financial transaction is posted:

Do NOT allow arbitrary editing.

Corrections must use controlled mechanisms:

```text
Original transaction
       ↓
Correction / reversal
       ↓
Replacement transaction
```

Audit trail must preserve:

* who
* what
* when
* previous value
* new value
* reason where applicable

Never "fix" financial history by directly modifying database records.

---

# 20. Dashboard

Initial dashboard:

```text
TODAY

Sales
PKR xxx

Collections
PKR xxx

Gross Profit
PKR xxx

Receivables
PKR xxx

Payables
PKR xxx

Cash
PKR xxx

Bank
PKR xxx
```

Monthly:

```text
Current Month

Sales
Collections
Costs
Gross Profit
Receivables
Payables
```

Charts:

* Sales by service
* Sales by salesperson
* Collections by payment method
* Revenue vs cost
* Receivables aging
* Payables aging

All dashboard numbers must be drill-down capable.

---

# 21. Required Reports

## Sales Report

Filters:

```text
Date
Branch
Salesperson
Service
Customer
Supplier
Status
```

Columns:

```text
Reference
Date
Customer
Service
Salesperson
Supplier
Selling
Cost
Profit
Paid
Outstanding
Status
```

---

## Customer Receivable Report

```text
Customer
Total Sales
Paid
Outstanding
Overdue
```

Clicking a customer must show underlying transactions.

---

## Supplier Payable Report

```text
Supplier
Total Cost/Bills
Paid
Outstanding
Overdue
```

---

## Profitability Report

By:

* service
* salesperson
* branch
* customer
* supplier
* date range

Formula:

```text
Revenue - Cost = Gross Profit
```

---

## Customer Statement

Example:

```text
Customer: Ahmed Khan

Date        Description       Debit    Credit   Balance

01-Sep      Ticket           150,000       -   150,000
03-Sep      Payment               -   50,000   100,000
05-Sep      Payment               -   30,000    70,000
```

---

## Supplier Statement

Same concept for supplier payable activity.

---

# 22. Branch Support

Even if Kamal currently has one branch, include branch as a first-class dimension.

```text
Company
  ├── Branch A
  ├── Branch B
  └── Branch C
```

Every relevant transaction should have a branch.

Do not build branch-specific hard-coded logic.

---

# 23. Existing Jotform Migration

Current Jotform fields should be mapped.

Known fields include approximately:

```text
Customer Name
Date
Serial Number
Service Type
Vendor
Country
Sector
Total Amount
Received Amount
Remaining Amount
Collector
```

Mapping:

```text
Jotform Customer Name
→ Customer

Jotform Date
→ Sale Date

Jotform Serial
→ External Reference

Jotform Service
→ Service

Jotform Vendor
→ Supplier

Jotform Country
→ Operational metadata

Jotform Sector
→ Operational metadata

Jotform Total
→ Selling Total

Jotform Received
→ Payment

Jotform Remaining
→ CALCULATED
```

IMPORTANT:

The imported "Remaining" value must NOT become the authoritative balance.

Recalculate:

```text
Remaining = Total - Payments
```

and flag discrepancies during migration.

---

# 24. Migration Strategy

Do not blindly import everything.

First:

1. Export Jotform submissions.
2. Analyze data quality.
3. Identify duplicates.
4. Normalize service names.
5. Normalize vendor names.
6. Normalize customer names.
7. Validate financial totals.
8. Import customers.
9. Import suppliers.
10. Import historical sales.
11. Import historical payments where reliable.
12. Reconcile balances.
13. Generate migration discrepancy report.

Migration must be reversible/testable.

---

# 25. Security

Minimum requirements:

* Role-based permissions
* Record-level access where appropriate
* No financial manipulation through UI
* Server-side validation
* Audit logging
* Controlled accounting posting
* No direct database writes by normal users
* Secrets only through environment/configuration
* Production credentials never committed to Git

---

# 26. Technical Architecture

Recommended module structure:

```text
addons/
│
├── alamia_travel_core/
│
├── alamia_travel_sales/
│
├── alamia_travel_finance/
│
└── alamia_travel_reporting/
```

Avoid one enormous:

```text
alamia_travel_os/
```

module containing everything.

Future modules can become:

```text
alamia_travel_ticketing/
alamia_travel_visa/
alamia_travel_appointments/
alamia_travel_hajj_umrah/
alamia_travel_documents/
alamia_travel_ai/
```

---

# 27. Odoo Reuse Rule

Before implementing a model, determine whether Odoo already provides the required primitive.

Prefer reuse of:

```text
res.partner
res.users
res.company
account.move
account.payment
account.account
account.journal
product.product
product.template
sale.order
```

or equivalent primitives appropriate to the selected Odoo Community version.

Do not duplicate standard Odoo accounting/customer/payment functionality without a documented reason.

Travel-specific models should contain travel-specific information.

---

# 28. Architecture Boundary

Travel OS:

```text
WHO
WHAT SERVICE
WHEN
FOR WHOM
SUPPLIER
OPERATIONAL STATUS
TRAVEL DETAILS
```

Odoo Accounting:

```text
HOW MUCH
RECEIVABLE
PAYABLE
REVENUE
COST
CASH
BANK
JOURNAL
ACCOUNTING STATE
```

Integration layer connects the two.

---

# 29. DAG

The implementation DAG is:

```text
S0
 │
 ├── S0.1 Odoo environment
 ├── S0.2 Git/repository
 ├── S0.3 Module skeleton
 └── S0.4 Technical conventions
        │
        ▼
S1
 │
 ├── S1.1 Company/Branch
 ├── S1.2 Roles/Permissions
 ├── S1.3 Customer foundation
 ├── S1.4 Supplier foundation
 └── S1.5 Service catalog
        │
        ▼
S2
 │
 ├── S2.1 Sale model
 ├── S2.2 Sale lines
 ├── S2.3 Sale workflow
 ├── S2.4 Cost model
 └── S2.5 Financial calculations
        │
        ▼
S3
 │
 ├── S3.1 Customer payments
 ├── S3.2 Partial payments
 ├── S3.3 Payment allocation
 ├── S3.4 Cash/bank journals
 └── S3.5 Accounting integration
        │
        ▼
S4
 │
 ├── S4.1 Supplier bills/costs
 ├── S4.2 Supplier payments
 ├── S4.3 Payable calculation
 └── S4.4 Supplier accounting integration
        │
        ▼
S5
 │
 ├── S5.1 Dashboard
 ├── S5.2 Sales reports
 ├── S5.3 Receivable reports
 ├── S5.4 Payable reports
 ├── S5.5 Profit reports
 └── S5.6 Statements
        │
        ▼
S6
 │
 ├── S6.1 Jotform import
 ├── S6.2 Data normalization
 ├── S6.3 Reconciliation
 └── S6.4 Migration validation
        │
        ▼
S7
 │
 ├── S7.1 E2E tests
 ├── S7.2 Accounting integrity tests
 ├── S7.3 Permission tests
 ├── S7.4 Migration tests
 └── S7.5 UAT
        │
        ▼
S8
 │
 ├── S8.1 Kamal pilot
 ├── S8.2 Feedback
 ├── S8.3 Fixes
 └── S8.4 Production readiness
```

---

# 30. Sprint Plan

## Sprint 0 — Environment & Architecture

### Goal

Get a clean Odoo development foundation.

### Tasks

* [ ] Verify Odoo Community version
* [ ] Pin Odoo image/version
* [ ] Verify PostgreSQL compatibility
* [ ] Establish Docker Compose
* [ ] Establish persistent volumes
* [ ] Establish custom addons directory
* [ ] Initialize Git repository
* [ ] Establish `.env.example`
* [ ] Establish development documentation
* [ ] Create module skeleton
* [ ] Establish coding conventions
* [ ] Establish test framework

### Exit Criteria

```text
docker compose up
        ↓
Odoo starts
        ↓
Database works
        ↓
Custom addon installs
        ↓
Automated test runs
```

---

# Sprint 1 — Core Master Data

### Goal

Create the foundation.

### Tasks

* [ ] Customer configuration
* [ ] Supplier configuration
* [ ] Branch model/configuration
* [ ] Service catalog
* [ ] User roles
* [ ] Access rights
* [ ] Basic navigation
* [ ] Customer list/form
* [ ] Supplier list/form
* [ ] Service list/form

### Tests

* [ ] Create customer
* [ ] Create supplier
* [ ] Create service
* [ ] Assign branch
* [ ] Permission enforcement

### Exit Criteria

A sales user can create/select a customer, supplier and service.

---

# Sprint 2 — Sales Engine

### Goal

Record actual travel sales.

### Tasks

* [ ] Sale model
* [ ] Sale lines
* [ ] Customer relation
* [ ] Supplier relation
* [ ] Service relation
* [ ] Salesperson
* [ ] Branch
* [ ] Selling price
* [ ] Supplier cost
* [ ] Gross profit
* [ ] Status lifecycle
* [ ] Validation rules
* [ ] Sale reference numbering

### Tests

* [ ] Create sale
* [ ] Multiple sale lines
* [ ] Calculate total
* [ ] Calculate cost
* [ ] Calculate gross profit
* [ ] Cancel sale
* [ ] Invalid negative values
* [ ] Required field validation

### Exit Criteria

A staff member can enter a complete sale without Excel/Jotform.

---

# Sprint 3 — Collections & Accounting

### Goal

Make money movement real.

### Tasks

* [ ] Customer payment model/integration
* [ ] Payment methods
* [ ] Cash journals
* [ ] Bank journals
* [ ] Payment allocation
* [ ] Partial payment
* [ ] Full payment
* [ ] Outstanding calculation
* [ ] Accounting posting
* [ ] Customer balance
* [ ] Receipt/reference
* [ ] Payment reversal/correction mechanism

### Critical tests

```text
Sale 100,000
Payment 40,000
Expected outstanding = 60,000
```

```text
Sale 100,000
Payment 100,000
Expected outstanding = 0
```

```text
Sale 100,000
Payment 40,000
Payment 60,000
Expected outstanding = 0
```

```text
Sale 100,000
Payment 120,000
Expected system = controlled overpayment handling
```

### Accounting test

Verify:

```text
AR increases by sale
Cash/Bank increases by payment
AR decreases by payment
```

### Exit Criteria

The accountant can maintain customer receivables using actual accounting transactions.

---

# Sprint 4 — Supplier Costs & Payables

### Goal

Know what Kamal owes vendors.

### Tasks

* [ ] Supplier cost
* [ ] Vendor bill integration
* [ ] Supplier payable
* [ ] Partial supplier payment
* [ ] Supplier payment
* [ ] Payable balance
* [ ] Supplier statement
* [ ] Cost allocation
* [ ] Profit calculation

### Test

```text
Selling = 150,000
Cost = 120,000

Gross profit = 30,000
```

Then:

```text
Supplier bill = 120,000
Supplier payment = 70,000

Payable = 50,000
```

### Exit Criteria

Management can see both:

```text
Customers owe us
```

and

```text
We owe suppliers
```

---

# Sprint 5 — Management Reporting

### Goal

Turn transactions into management visibility.

### Tasks

* [ ] Executive dashboard
* [ ] Daily sales
* [ ] Monthly sales
* [ ] Collections
* [ ] Receivables
* [ ] Payables
* [ ] Gross profit
* [ ] Sales by service
* [ ] Sales by salesperson
* [ ] Sales by branch
* [ ] Customer statement
* [ ] Supplier statement
* [ ] Date filters
* [ ] Drill-down

### Exit Criteria

Management can answer the ten core financial questions without Excel.

---

# Sprint 6 — Jotform Migration

### Goal

Move existing operational history safely.

### Tasks

* [ ] Export Jotform data
* [ ] Analyze schema
* [ ] Normalize customers
* [ ] Normalize suppliers
* [ ] Normalize services
* [ ] Detect duplicate customers
* [ ] Map fields
* [ ] Import customers
* [ ] Import suppliers
* [ ] Import sales
* [ ] Import payments
* [ ] Recalculate balances
* [ ] Produce discrepancy report
* [ ] Reconcile imported balances

### Exit Criteria

Imported records reconcile against Jotform source totals.

---

# Sprint 7 — QA & Accounting Integrity

### Goal

Prove the system is financially trustworthy.

### Required test classes

## Functional

* Customer creation
* Supplier creation
* Sale creation
* Payment
* Supplier cost
* Supplier payment
* Reporting

## Accounting

* Revenue
* AR
* AP
* Cash
* Bank
* Cost
* Gross profit
* Reversal
* Partial payment
* Overpayment

## Integrity

Test invariants:

```text
Outstanding
=
Selling Total - Allocated Payments
```

```text
Gross Profit
=
Selling Total - Cost Total
```

```text
Customer Balance
=
Opening Balance
+
Debits
-
Credits
```

```text
Supplier Balance
=
Opening Balance
+
Credits
-
Payments
```

Exact formulas must follow the Odoo accounting representation actually implemented.

## Security

* Salesperson cannot modify unauthorized records
* Accountant permissions
* Manager permissions
* Posted accounting records protected
* Unauthorized API access denied

---

# Sprint 8 — Kamal UAT / Pilot

### Goal

Put the system in front of actual Kamal users.

### UAT scenarios

1. Create customer
2. Create ticket sale
3. Receive partial payment
4. Receive second payment
5. Create visa sale
6. Add supplier cost
7. Pay supplier
8. Check customer balance
9. Check supplier balance
10. Check daily sales
11. Check monthly sales
12. Check gross profit
13. Print/export statement
14. Correct an error
15. Cancel transaction
16. Verify audit history

### Exit Criteria

Kamal staff can perform normal daily operations without developer intervention.

---

# 31. End-to-End Golden Scenario

This must become one of the permanent regression tests.

```text
CUSTOMER
Ahmed Khan

SERVICE
Ticket

SELLING PRICE
150,000

SUPPLIER COST
120,000
```

Create sale.

Expected:

```text
Revenue = 150,000
Cost = 120,000
Gross Profit = 30,000
Receivable = 150,000
Payable = 120,000
```

Customer pays:

```text
80,000
```

Expected:

```text
Customer Receivable = 70,000
```

Supplier paid:

```text
50,000
```

Expected:

```text
Supplier Payable = 70,000
```

Management dashboard should reflect:

```text
Sales = 150,000
Collections = 80,000
Customer Receivable = 70,000
Supplier Payable = 70,000
Gross Profit = 30,000
```

All figures must drill down to source transactions.

---

# 32. Second Golden Scenario — Multiple Payments

```text
Sale = 200,000
Cost = 150,000
```

Payments:

```text
50,000
70,000
80,000
```

Expected:

```text
Paid = 200,000
Outstanding = 0
Gross Profit = 50,000
```

Accounting must reconcile.

---

# 33. Third Golden Scenario — Multiple Sales / Customer Balance

```text
Sale A = 100,000
Sale B = 200,000
Sale C = 50,000
```

Payments:

```text
100,000
50,000
```

Expected:

```text
Total Sales = 350,000
Paid = 150,000
Outstanding = 200,000
```

Customer statement must match.

---

# 34. Fourth Golden Scenario — Supplier Balance

```text
Vendor A
Cost 100,000
Cost 50,000
Cost 75,000

Total payable = 225,000
```

Payments:

```text
100,000
50,000
```

Expected:

```text
Outstanding = 75,000
```

Supplier statement must match.

---

# 35. Fifth Golden Scenario — Profitability

```text
Ticket A
Revenue = 150,000
Cost = 120,000

Visa B
Revenue = 50,000
Cost = 20,000

Hotel C
Revenue = 100,000
Cost = 70,000
```

Expected:

```text
Total Revenue = 300,000
Total Cost = 210,000
Gross Profit = 90,000
```

Service report:

```text
Ticket   → 30,000
Visa     → 30,000
Hotel    → 30,000
```

---

# 36. Definition of Done

Phase 1 is NOT complete merely because screens exist.

It is complete when:

* [ ] Staff can enter real transactions
* [ ] Customer balances are correct
* [ ] Supplier balances are correct
* [ ] Payments affect balances correctly
* [ ] Partial payments work
* [ ] Accounting entries are correct
* [ ] Revenue is correct
* [ ] Cost is correct
* [ ] Gross profit is correct
* [ ] Cash/bank balances are traceable
* [ ] Reports reconcile with underlying transactions
* [ ] Posted transactions cannot be silently altered
* [ ] Audit trail exists
* [ ] Permissions work
* [ ] Jotform data can be migrated/reconciled
* [ ] E2E tests pass
* [ ] Kamal users can complete daily workflows

---

# 37. Non-Negotiable Engineering Rules

## Rule 1

Do not duplicate Odoo accounting.

## Rule 2

Do not store calculated financial balances as manually editable truth.

## Rule 3

Do not allow direct database manipulation as a normal correction mechanism.

## Rule 4

Do not hard-code Kamal-specific business logic into the generic Travel OS.

## Rule 5

Do not implement future Ticketing/Visa/Hajj complexity prematurely.

## Rule 6

Every financial number must have a traceable source transaction.

## Rule 7

Every important dashboard number must be drill-down capable.

## Rule 8

Every financial mutation requires an audit trail.

## Rule 9

Business rules must have automated tests.

## Rule 10

Prefer Odoo-native mechanisms over custom replacements.

---

# 38. Future Extension Boundary

After Phase 1:

```text
                 ALAMIA TRAVEL OS
                         │
        ┌────────────────┼─────────────────┐
        │                │                 │
      CORE             FINANCE          REPORTING
        │
        ├── SALES
        │
        ├── TICKETING
        │
        ├── VISA
        │
        ├── APPOINTMENTS
        │
        ├── HAJJ
        │
        ├── UMRAH
        │
        ├── HOTELS
        │
        ├── DOCUMENTS
        │
        └── AI
```

Phase 1 must therefore establish the reusable foundation without attempting to implement all these verticals.

---

# 39. Final Product Test

The ultimate Phase-1 test is:

> Give the system to a Kamal Express accountant and sales employee and let them operate a normal business day.

At the end of the day management should be able to open the system and answer:

1. What did we sell today?
2. What did we collect today?
3. Who bought from us?
4. Who still owes us?
5. What do we owe suppliers?
6. What services generated revenue?
7. What services generated profit?
8. How much cash was collected?
9. How much went through banks?
10. What is our current financial position?
11. Which transactions need attention?
12. Can every number be traced to a transaction?

If the answer to all twelve is **yes**, Phase 1 has succeeded.

---

# 40. Immediate Agent Instruction

The agent should execute in this order:

```text
1. Finish Odoo Community local Docker setup
2. Verify exact Odoo version
3. Establish Git + addon structure
4. Implement Sprint 0
5. Implement Sprint 1
6. Stop and run tests
7. Implement Sprint 2
8. Stop and run tests
9. Implement Sprint 3
10. Run accounting integrity tests
11. Implement Sprint 4
12. Implement Sprint 5
13. Only then implement Jotform migration
14. Run complete E2E suite
15. Prepare Kamal UAT
```

**Do not jump ahead to AI, WhatsApp, Ticketing automation, Visa automation, or fancy dashboards until the accounting/transaction backbone passes the golden scenarios.**

The system's first job is to make Kamal's financial state **trustworthy**. Everything else comes after that.
