We are migrating historical Kamal Express Excel data into the existing Odoo Travel OS.

IMPORTANT:

* Use the installed Odoo MCP to inspect and modify Odoo.
* Use the Kamal Express Excel workbook already available in the project.
* Do NOT attempt the entire migration at once.
* Work incrementally.
* After every batch, verify the result in Odoo before continuing.
* Do not invent data.
* Do not create duplicate records.
* Do not modify accounting transactions yet.

## TASK 2 — Create Service Catalogue Records

Inspect Odoo and create the canonical service catalogue defined in Task 1.

Use Odoo MCP to:

1. **Create missing service categories** (if not already existing from Task 1 inspection):
   - Ticketing
   - Visa
   - Hotel
   - Insurance
   - Appointment
   - Hajj
   - Umrah
   - Apostille
   - Attestation
   - Case Preparation
   - Consultancy
   - Other

2. **Create missing canonical services** mapped from raw Excel labels:
   - For each category, create services with normalized names
   - Preserve original raw labels in the mapping for traceability

3. **Reuse existing records** where categories/services already exist in Odoo

### Mapping Example (from Task 1):

| RAW EXCEL LABEL | CATEGORY | SERVICE |
|----------------|----------|---------|
| Saudi Visit Visa | Visa | Visit Visa |
| Visit Visa | Visa | Visit Visa |
| Saudi Visa | Visa | Visit Visa |
| Visa Saudia | Visa | Visit Visa |
| Country/subservice: Saudi Arabia | Visa | Visit Saudi |

### BEFORE CREATING ANYTHING

Show me a proposed mapping table:

RAW EXCEL LABEL → CATEGORY → SERVICE

Then inspect Odoo and determine which records already exist. Avoid duplicates.

## CREATE

Using Odoo MCP:

1. Create missing service categories (see list above)
2. Create missing canonical services under each category
3. Reuse existing records where appropriate

Do not create sales, customers, invoices or payments yet.

## VERIFY

After creation, use Odoo MCP to query the records again.

Verify:

* category exists
* service exists
* correct category relationship
* no duplicates
* all created records have valid names

Then produce a concise report:

Created:

* X categories
* X services

Reused:

* X existing records

Skipped:

* X duplicates

Needs review:

* X ambiguous mappings

STOP after this task.

Do not proceed to customers until this task is verified.