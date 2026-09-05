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

## TASK 1 — Build the Service Catalogue

First inspect the existing Odoo Travel OS models and determine how services/categories are currently represented.

Use Odoo MCP to inspect:

* existing service categories
* existing services/products
* fields
* IDs
* existing records

Then inspect the Kamal Express workbook and extract the unique service labels.

Normalize the raw labels into a small canonical service catalogue.

Initial categories should cover at least:

* Ticketing
* Visa
* Hotel
* Insurance
* Appointment
* Hajj
* Umrah
* Apostille
* Attestation
* Case Preparation
* Consultancy
* Other

Do NOT blindly create every raw Excel label as a separate service.

For example:

"Saudi Visit Visa"
"Visit Visa"
"Saudi Visa"
"Visa Saudia"

may map to:

Category: Visa
Service: Visit Visa
Country/subservice: Saudi Arabia

Preserve the original raw labels in the migration mapping so we can trace them.

## BEFORE CREATING ANYTHING

Show me a proposed mapping:

RAW EXCEL LABEL → CATEGORY → SERVICE

Then inspect Odoo and determine which records already exist.

Avoid duplicates.

## CREATE

Using Odoo MCP:

1. Create missing service categories.
2. Create missing canonical services.
3. Reuse existing records where appropriate.

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
