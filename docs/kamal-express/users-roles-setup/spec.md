# Sprint: Kamal Express Users, Roles & Dashboards

## Objective

Configure the initial Kamal Express users in Alamia Travel OS / Odoo Community with role-based access.

The system must distinguish **organizational role** from **operational permissions**.

Important: CEO, Operations Director, and Assistant Operations/Marketing users may all create sales/invoices despite having different organizational roles.

---

## 1. Users

Create these five users:

| User             | Email                                                       | Role                                     |
| ---------------- | ----------------------------------------------------------- | ---------------------------------------- |
| Syed Kamal Ahmed | [kamal@kamalexpress.com](mailto:kamal@kamalexpress.com)     | CEO                                      |
| Malik Jawad      | [jawad@kamalexpress.com](mailto:jawad@kamalexpress.com)     | Head/Director of Operations              |
| Ali Raza         | [ali@kamalexpress.com](mailto:ali@kamalexpress.com)         | Head/Director of IT & Software           |
| Tayyab           | [tayyab@kamalexpress.com](mailto:tayyab@kamalexpress.com)   | Assistant Manager Operations & Marketing |
| Zeeshan          | [zeeshan@kamalexpress.com](mailto:zeeshan@kamalexpress.com) | Head/Director Sales & Customer Relations |

Use the email addresses as the login identifiers.

Do not hard-code passwords into the repository. Initial passwords/reset links must be handled through Odoo's normal secure user provisioning/reset mechanism.

---

# 2. Roles

Create five application roles/groups:

### CEO

`travel_role_ceo`

### Head/Director Operations

`travel_role_operations_director`

### Head/Director IT & Software

`travel_role_it_director`

### Assistant Manager Operations & Marketing

`travel_role_operations_marketing`

### Head/Director Sales & Customer Relations

`travel_role_sales_director`

---

# 3. Sales / Invoice Access

The following users **must be able to create and manage normal sales transactions**:

* Syed Kamal Ahmed
* Malik Jawad
* Tayyab
* Zeeshan

They need access to:

* Customers
* Sales
* Sale forms
* Sale lines
* Invoicing workflow
* Customer payments/collections where permitted
* Customer balances
* Relevant sales reports

This requirement overrides simplistic role assumptions.

For example:

> CEO is not merely a read-only executive role.

The CEO may personally create a sale.

---

# 4. CEO Permissions

### Access

* Full operational visibility
* All customers
* All sales
* All invoices
* All collections
* All suppliers
* All payables
* All financial reports
* All management dashboards
* All branches
* Accounting visibility
* User/role visibility where appropriate

### Restrictions

The CEO should **not bypass accounting controls** merely because of the CEO role.

Posted accounting records must still follow Odoo's controlled correction/reversal mechanisms.

---

# 5. Operations Director Permissions

Malik Jawad:

### Full operational access

* Customers
* Sales
* Invoices
* Payments/collections
* Suppliers
* Supplier-related transactions
* Operational records
* Documents
* Sales reports
* Receivable reports
* Payable reports
* Operations dashboard

### Visibility

All operational transactions across the company/assigned branches.

He can personally create sales.

---

# 6. Sales & Customer Relations Director

Zeeshan:

### Primary access

* Customers
* Customer history
* Sales
* Invoices
* Collections
* Customer balances
* Sales reports
* Salesperson performance
* Documents relevant to customers

### Restrictions

Should not have unrestricted accounting configuration/admin access.

He can create sales.

He should be able to see enough financial information to understand:

* sale value
* amount received
* customer outstanding
* transaction profitability where authorized

---

# 7. Assistant Manager Operations & Marketing

Tayyab:

### Access

* Customers
* Sales
* Invoices
* Collections
* Operational records
* Documents
* Relevant sales reports
* Customer balances

He can create sales.

### Restrictions

No:

* system administration
* accounting configuration
* user/role administration
* unrestricted financial configuration

---

# 8. IT & Software Director

Ali Raza:

This is the technical/admin role.

### Access

* Odoo administration
* Technical configuration
* Modules
* Users
* Security/access configuration
* System configuration
* Logs/debugging where appropriate
* All application areas required for development/maintenance

### Dashboard

**NO dedicated business dashboard.**

Ali should land on the normal technical/application administration interface rather than a CEO/Operations/Sales dashboard.

### Important

IT access must not be interpreted as permission to modify accounting data directly in the database.

Financial integrity rules apply to everyone.

---

# 9. Dashboard Requirement

Each business role gets its own dashboard.

## CEO Dashboard

Widgets:

```text
Today's Sales
Today's Collections
Monthly Sales
Monthly Gross Profit
Total Receivables
Total Payables
Cash Position
Bank Position
Sales by Service
Sales by Staff
```

Include drill-down into underlying transactions.

---

## Operations Director Dashboard

Focus on operations + financial control:

```text
Today's Sales
Today's Collections
Pending Transactions
Outstanding Customer Balances
Supplier Payables
Sales by Service
Sales by Staff
Operational Workload
Recent Transactions
```

---

## Sales Director Dashboard

Focus on customers and sales:

```text
Today's Sales
Monthly Sales
My/Team Sales
Collections
Outstanding Customer Balances
Sales by Service
Top Customers
Recent Sales
Salesperson Performance
```

---

## Assistant Manager Operations & Marketing Dashboard

Focus on daily execution:

```text
Today's Sales
Today's Collections
Recent Customers
Recent Sales
Pending Operational Items
Customer Outstanding
Sales by Service
My Sales
```

---

## IT Director

No custom business dashboard.

---

# 10. Dashboard Architecture

Do not create four completely independent dashboard implementations.

Create a reusable dashboard framework:

```text
Travel Dashboard
       │
       ├── CEO configuration
       ├── Operations configuration
       ├── Sales configuration
       └── Operations/Marketing configuration
```

Widgets should reuse the same underlying reporting services/queries.

Permissions must be applied at the data layer.

**Never rely on hiding dashboard widgets as the security mechanism.**

---

# 11. Access Matrix

| Capability         |          CEO |    Ops Dir |    IT Dir | Ops/Marketing |   Sales Dir |
| ------------------ | -----------: | ---------: | --------: | ------------: | ----------: |
| Customers          |         Full |       Full |     Admin |   Create/Edit |        Full |
| Sales              |         Full |       Full |     Admin |   Create/Edit |        Full |
| Invoices           |         Full |       Full |     Admin |   Operational | Operational |
| Customer Payments  |         Full |       Full |     Admin |   Create/View | Create/View |
| Suppliers          |         Full |       Full |     Admin |       Limited |        View |
| Payables           |         Full |       Full |     Admin |          View |        View |
| Sales Reports      |         Full |       Full |     Admin |      Relevant |        Full |
| Financial Reports  |         Full |       Full |     Admin |       Limited |    Relevant |
| Users              | Admin/Manage |         No |      Full |            No |          No |
| System Config      |      Limited |         No |      Full |            No |          No |
| Accounting Config  |   Controlled | Controlled | Technical |            No |          No |
| Business Dashboard |          CEO | Operations |  **None** | Ops/Marketing |       Sales |

"Admin" in this table means technical/system access where appropriate; it must **not** provide a mechanism for silently altering posted accounting history.

---

# 12. Record Visibility

Implement permissions using Odoo access groups and record rules.

Default principle:

```text
CEO
   ↓
All company data

Operations Director
   ↓
All operational/company data

Sales Director
   ↓
Customer + sales data

Operations/Marketing
   ↓
Operational/customer data

IT
   ↓
Technical administration
```

Do not over-restrict the initial Kamal deployment if they operate as one company/branch.

The architecture must nevertheless support future branch-level restrictions.

---

# 13. Acceptance Tests

### User provisioning

* [ ] All five users exist
* [ ] Correct email/login
* [ ] Correct role/group
* [ ] Secure initial password provisioning
* [ ] Users can log in

### Sales

Verify each of:

* [ ] CEO can create a sale
* [ ] Operations Director can create a sale
* [ ] Tayyab can create a sale
* [ ] Zeeshan can create a sale

### Dashboard

* [ ] CEO sees CEO dashboard
* [ ] Operations Director sees Operations dashboard
* [ ] Zeeshan sees Sales dashboard
* [ ] Tayyab sees Operations/Marketing dashboard
* [ ] Ali does NOT receive a dedicated business dashboard

### Security

* [ ] Sales users cannot access system administration
* [ ] Sales users cannot modify accounting configuration
* [ ] Operations/Marketing cannot manage users
* [ ] Sales Director cannot alter posted accounting records
* [ ] Dashboard visibility cannot expose unauthorized records
* [ ] Direct URL/API attempts are still permission-checked

### Data consistency

Create a test sale as each authorized sales user and verify:

```text
Sale
  ↓
Invoice
  ↓
Payment
  ↓
Customer Balance
  ↓
Dashboard
  ↓
Reports
```

All numbers must remain consistent.

---

# 14. Definition of Done

This sprint is complete only when:

1. All five users can log in.
2. Their organizational roles are correctly represented.
3. CEO, Operations Director, Tayyab and Zeeshan can create sales/invoices.
4. Appropriate customer/payment access exists.
5. Each business role lands on the correct dashboard.
6. Ali has no dedicated business dashboard.
7. Permissions are enforced server-side.
8. Accounting configuration remains protected.
9. Posted financial transactions remain protected.
10. Automated permission tests pass.
11. Dashboard figures use the same underlying financial/operational data as reports.
12. No Kamal-specific credentials are committed to source control.

---

# 15. Implementation Constraint

Before creating custom role/group logic, inspect Odoo Community's existing:

* Users
* Groups
* Access Control Lists
* Record Rules
* Accounting groups
* Sales/Invoicing permissions

Extend/reuse existing Odoo mechanisms where possible.

Do not create a parallel authentication or authorization system.

---

# 16. Sprint Output

Agent must provide:

```text
1. Users created
2. Groups/roles created
3. Access matrix implemented
4. Dashboards implemented
5. Security rules implemented
6. Automated permission tests
7. Screenshot/demo of each dashboard
8. Test report
9. List of Odoo-native groups reused
10. List of custom groups/rules created
```

After this sprint, the system should be ready for the next major Phase-1 workstream: **Sales → Invoice → Payment → Receivable → Supplier Cost → Payable → Profitability**.
