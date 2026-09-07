## Objective

Customize the Odoo system so that **every operational role has a role-specific, action-oriented dashboard** that helps the employee know:

1. **What I need to do today**
2. **What is overdue**
3. **What is coming next**
4. **What requires my attention**
5. **What work I have completed**
6. **What important items I might otherwise forget**

The dashboard should function as a **daily work cockpit**, not merely a reporting/KPI screen.

---

# 1. Core Requirement: "Today’s Work"

Every role dashboard must have a prominent **Today / My Work** section.

It should surface actionable items such as:

- Calls to make
- Meetings/appointments
- Follow-ups
- Emails/messages to send
- Customer payments to follow up
- Documents to collect
- Visa/application tasks
- Booking/ticketing tasks
- Pending approvals
- Tasks assigned by management
- Overdue activities
- Activities due today
- Upcoming activities
- Items waiting for the employee's action

Each item should be **clickable** and take the user directly to the relevant Odoo record/action.

Example:

> **Today — 7 Items**
>
> 🔴 2 Overdue  
> 🟠 3 Due Today  
> 🔵 2 Upcoming
>
> **Call Tayyab — Pending Payment — Customer XYZ**  
> Due: Today, 11:00 AM  
> [Open Customer] [Mark Done] [Reschedule]

---

# 2. Activities Must Drive the Dashboard

Use Odoo's existing **Activities / activity scheduling mechanism** wherever possible instead of creating a parallel task system.

For example, when an administrator assigns:

> Call Tayyab → Customer ABC → Ask customer to clear pending amount → Due today

Tayyab's dashboard should automatically show:

### Today's Tasks

**Call Customer ABC**

Purpose: Follow up on pending payment  
Assigned by: Admin  
Due: Today  
Priority: High

Actions:

- Open Customer
- Call
- Add Note
- Mark Done
- Schedule Next Activity

The employee should **not need to manually search through Contacts, Invoices, Sales Orders, etc. to discover their work.**

---

# 3. Role-Based Dashboards

Create dashboards according to the actual roles configured in the system.

Do not create generic dashboards containing every Odoo feature.

Each role should see only the information relevant to their daily responsibilities.

Initially support at least:

### CEO / Chairman

Focus on:

- Business overview
- Today's important issues
- Sales today / this month
- Outstanding receivables
- Outstanding payables
- Pending approvals
- Important overdue items
- Sales pipeline
- Operational alerts
- Staff workload / pending work
- Recent activity
- High-value customers
- Exception alerts

The CEO dashboard should answer:

> **"Is the business under control?"**

---

### Operations / Operations Manager

Focus on:

- Today's operational tasks
- Pending bookings
- Pending ticketing work
- Pending visa applications
- Upcoming departures
- Customer follow-ups
- Missing documents
- Payment issues
- Overdue activities
- Staff tasks
- Operational exceptions
- Recently completed work

Answer:

> **"What operational work needs attention today?"**

---

### Sales / Customer Relations

Focus on:

- Today's calls
- Follow-ups due today
- Overdue follow-ups
- New leads/customers
- Customers awaiting response
- Pending payments
- Quotations
- Sales opportunities
- Upcoming customer commitments
- Recent interactions

Answer:

> **"Who do I need to contact and what do I need to do to move the sale forward?"**

---

### Marketing

Focus on:

- Today's marketing tasks
- Campaign activities
- Leads generated
- Lead sources
- Follow-ups
- Campaign performance
- Pending content/tasks
- Upcoming marketing activities

---

### Ticketing / Travel Agent

Focus on:

- Today's bookings
- Pending ticket issuance
- Upcoming flights
- Booking confirmations
- Payment pending
- Customer documents pending
- Airline-related tasks
- Follow-ups
- Overdue activities

---

### Visa / Documentation Staff

Focus on:

- Applications requiring action
- Documents missing
- Documents expiring
- Applications pending
- Applications requiring follow-up
- Today's tasks
- Upcoming deadlines
- Completed applications

---

### Accounts / Accountant

Focus on:

- Today's accounting tasks
- Unpaid invoices
- Overdue receivables
- Payables
- Pending payments
- Bank/cash activity
- Reconciliation tasks
- Recent vouchers
- Accounting exceptions
- Month-to-date financial summary

---

### IT / Administrator

Focus on:

- System alerts
- Assigned tasks
- User requests
- Integration/API errors
- Failed scheduled jobs
- System health
- Pending configuration tasks
- Recent administrative activities

Do not unnecessarily expose operational/business data to IT unless their role requires it.

---

# 4. Dashboard Widget Standards

Every dashboard should follow a consistent structure.

## Section A — My Day

The most important section.

Show:

- Overdue
- Due Today
- Due Tomorrow
- Upcoming

Sort by:

1. Overdue
2. High priority
3. Due time
4. Normal tasks

---

## Section B — Quick Actions

Provide large, obvious shortcuts relevant to the role.

Examples:

**Sales**

- New Customer
- New Lead
- Schedule Call
- Create Quotation
- Record Payment
- Search Customer

**Operations**

- New Booking
- New Visa Application
- New Ticket
- Schedule Activity
- Search Customer

**Accounts**

- New Invoice
- New Payment
- New Voucher
- Customer Ledger
- Trial Balance

---

## Section C — Attention Required

Automatically surface exceptions.

Examples:

- 5 overdue activities
- 3 customers awaiting response
- 4 unpaid invoices overdue
- 2 visa applications missing documents
- 3 bookings awaiting confirmation

This section should answer:

> **"What could go wrong if I ignore it?"**

---

## Section D — Upcoming

Show important upcoming work:

- Tomorrow
- Next 7 days
- Upcoming customer commitments
- Departures
- Visa deadlines
- Payment deadlines
- Scheduled calls/meetings

---

## Section E — Performance / Summary

Only include KPIs that actually help the employee.

Avoid filling dashboards with meaningless charts.

Examples:

- Tasks completed today
- Tasks remaining
- Follow-ups completed
- Sales this month
- Collections this month
- Applications processed
- Bookings completed

---

# 5. Activity Lifecycle

Implement a clear activity workflow:

**Scheduled → Due → Completed**

with overdue detection.

When an activity is completed, encourage the employee to:

1. Record the outcome
2. Add relevant notes
3. Optionally schedule the next activity

Example:

> Call customer → Customer requested 2 days → Mark Done → Schedule follow-up for Thursday.

This creates a continuous workflow rather than isolated activities.

---

# 6. "Nothing Gets Forgotten" Mechanism

This is a critical requirement.

The system should proactively surface work that has not been completed.

Examples:

### Overdue Activities

> 🔴 4 activities are overdue

Clicking it should open the employee's overdue activities.

### Unresolved Customer Follow-ups

If a customer interaction requires another action, the system should encourage/suggest scheduling the next activity.

### Pending Payments

If a customer has an outstanding amount, relevant staff should see a follow-up requirement.

### Upcoming Deadlines

Items approaching their deadline should become increasingly visible.

Use appropriate Odoo activity types, priorities, deadlines and reminders rather than building unnecessary custom mechanisms.

---

# 7. Role Permissions

Dashboards must respect Odoo security rules.

A user should only see:

- Records they are allowed to access
- Activities assigned to them
- Relevant team/company information according to their permissions

Managers may see team-level workload.

Example:

### Staff

> My 7 activities

### Operations Manager

> My 5 activities  
> Team: 18 pending  
> Overdue: 4

### CEO

> Organization-wide critical items

Do not bypass Odoo's access control merely to populate dashboards.

---

# 8. Manager Visibility

Managers should have a **Team Workload** widget.

Example:

| Staff | Today | Overdue | Upcoming |
|---|---:|---:|---:|
| Tayyab | 5 | 2 | 3 |
| Zeeshan | 7 | 0 | 4 |
| Staff A | 3 | 1 | 5 |

Clicking an employee should show their assigned activities/work.

This is particularly important because management should be able to detect:

- Forgotten tasks
- Overloaded staff
- Repeatedly overdue work
- Unassigned work
- Work waiting too long

---

# 9. Notifications / Reminders

Where practical, integrate with Odoo's existing notification/activity mechanisms.

Do not rely exclusively on employees opening the dashboard.

Important activities should generate appropriate Odoo reminders/notifications.

However, avoid notification spam.

The dashboard should remain the **single source of truth for actionable work**.

---

# 10. UI/UX Requirement

The dashboard should feel like a modern productivity application.

Prioritize:

- Clear hierarchy
- Large actionable cards
- Minimal clutter
- Status indicators
- Priority indicators
- Due dates/times
- One-click navigation
- Quick actions
- Search
- Responsive layout

Avoid:

- Decorative charts
- Vanity metrics
- Huge amounts of unused whitespace
- Showing every Odoo menu
- Requiring users to navigate through multiple screens to find their work

The first thing a user should see after logging in should be:

> **"Here is what you need to do."**

---

# 11. Important: Discover Existing Odoo Capabilities First

Before writing custom modules, inspect the current Odoo installation and determine what can be achieved using:

- Activities
- Activity types
- Calendar
- CRM
- Sales
- Contacts
- Accounting
- Project/Tasks where appropriate
- Search views
- Filters
- Kanban views
- List views
- Existing dashboards
- Odoo Studio/custom views if available
- Automated actions
- Scheduled actions
- Notifications

**Do not rebuild functionality that already exists in Odoo.**

Only create custom models/widgets where the standard functionality genuinely cannot satisfy the requirement.

---

# 12. Use Real System Data

Do not build a fake dashboard using hardcoded/demo data.

Use the actual Odoo database.

Test the dashboard with real users/roles currently configured in the system.

Specifically test the scenario:

1. Admin logs in.
2. Admin opens a customer.
3. Admin schedules an activity for Tayyab.
4. Activity type = Call.
5. Description = Follow up regarding pending payment.
6. Due date = Today.
7. Tayyab logs in.
8. Tayyab immediately sees the task on his dashboard.
9. Tayyab opens the customer from the dashboard.
10. Tayyab completes the call.
11. Tayyab records the outcome.
12. Tayyab schedules another follow-up if required.
13. Dashboard updates automatically.

This scenario is a **mandatory acceptance test**.

---

# 13. Acceptance Criteria

The implementation is NOT complete merely because different dashboards exist.

It is complete when:

- Every important role has a relevant dashboard.
- Each dashboard prioritizes actionable work.
- Assigned activities automatically appear for the assigned employee.
- Overdue activities are clearly visible.
- Today's activities are immediately visible.
- Upcoming work is visible.
- Users can open the underlying record directly.
- Users can complete/reschedule activities from the workflow.
- Managers can see team workload where appropriate.
- Dashboard information respects Odoo permissions.
- No important work is hidden behind unnecessary navigation.
- No major dashboard widget is populated with fake/hardcoded data.
- The system works with actual production records.
- The "Admin assigns task → Employee sees task → Employee completes task" workflow works end-to-end.

---

# 14. Development Approach

Before implementing, inspect the current Odoo modules, installed custom modules, user groups, models and existing UI.

Then produce a short implementation plan identifying:

1. What can be achieved using standard Odoo.
2. What requires configuration.
3. What requires custom development.
4. Which models/views will be modified.
5. Which dashboards/widgets will be created.
6. Any security/access-control implications.

Then implement incrementally.

**Do not make broad changes to the existing Odoo system before understanding the current architecture.**

The goal is not simply to make Odoo look better.

The goal is to make Odoo behave like an **operational work-management system where employees know what to do, managers know what is pending, and important customer/business follow-ups are difficult to forget.**