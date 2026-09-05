# Kamal Express Excel Classification & Import Pipeline

## Objective

We need to turn the existing Kamal Express Excel ledger into clean, importable Travel OS data.

The source workbook is:

`ledger sheet KAMAL EXPRESS.xlsx`

A preliminary classified staging workbook has also been produced:

`kamal_express_classified_import_staging.xlsx`

The ultimate goal is to be able to reliably import:

1. **Clients / Parties**
2. **Services**
3. **Sales / Transactions**
4. **Customer Payments**, where supported by evidence
5. **Supplier / Vendor information**
6. **Expenses**, separately from sales

The local model available for fuzzy classification/normalization is:

`qwen3.5:4b`

via local Ollama.

---

# CRITICAL ARCHITECTURE RULE

Do NOT build this as:

`Excel → LLM → Odoo`

Build:

`Excel → deterministic parser → normalized staging → Qwen classification where required → deterministic validation → import candidates → Odoo`

The LLM must NEVER be the authority for:

* arithmetic
* balances
* totals
* payment amounts
* dates when a deterministic date can be extracted
* duplicate IDs
* accounting entries
* whether money was actually received
* whether a transaction should be posted

Qwen is an **interpretation/classification assistant**, not an accounting engine.

---

# Phase 0 — Inspect the Existing Project

Before writing code:

1. Inspect the repository.
2. Identify the existing Travel OS modules/models.
3. Identify existing:

   * Customer/Party model
   * Supplier model
   * Service model
   * Sale model
   * Sale Line model
   * Payment model
   * Expense model
4. Identify whether an existing import/staging framework already exists.
5. Reuse existing models and services wherever possible.

Do NOT create duplicate entities if the Travel OS already has them.

Produce a short implementation note before modifying code.

---

# Phase 1 — Inspect the Workbook

Use Python/openpyxl/pandas for workbook inspection.

Do NOT send the workbook wholesale to Qwen.

Inspect every worksheet and determine:

* sheet name
* number of rows
* number of columns
* headers
* apparent date columns
* customer/name columns
* service columns
* vendor/supplier columns
* amount columns
* payment/received columns
* remaining/balance columns
* collector/staff columns
* notes
* expense-like rows
* malformed rows

Preserve:

`source_file`

`source_sheet`

`source_row`

for every extracted record.

This source lineage is mandatory.

---

# Phase 2 — Create Canonical Data Model

Create normalized staging structures.

## PartyCandidate

Fields:

* source_id
* source_sheet
* source_row
* raw_name
* normalized_name
* party_type

  * customer
  * supplier
  * unknown
* phone
* email
* country
* notes
* confidence
* review_required
* classification_reason

Do not invent phone/email information.

---

## ServiceCandidate

Fields:

* source_label
* normalized_label
* canonical_service
* category
* confidence
* review_required
* source_occurrences

Initial canonical service categories should include at least:

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

Do not destroy the original service label.

Example:

```text
raw:
"Visit Visa Saudi"

canonical:
"Visa"

subservice:
"Saudi Visit Visa"
```

Where useful, retain:

* service_category
* service_name
* subservice

---

# Phase 3 — Sales Classification

Every potential transaction must become a `SaleCandidate`.

Fields:

* source_id
* source_sheet
* source_row
* sale_date
* external_reference
* customer_raw
* customer_candidate
* service_raw
* service_candidate
* supplier_raw
* supplier_candidate
* country
* sector
* salesperson
* selling_amount
* received_amount
* remaining_amount_raw
* calculated_remaining
* cost_amount
* profit_amount
* notes
* confidence
* review_required
* classification_reason

Important:

## Never trust manually entered Remaining Amount.

Always calculate:

```text
calculated_remaining =
    selling_amount - valid_received_amount
```

If the source says a different remaining amount, record:

```text
source_remaining_amount
calculated_remaining_amount
discrepancy_amount
```

and flag it.

---

# Phase 4 — Deterministic Extraction First

Before asking Qwen anything, attempt deterministic extraction.

Examples:

### Amounts

Recognize:

```text
150000
150,000
PKR 150000
18+9
42000+800 ins
```

But DO NOT automatically assume every expression is a sale total.

For ambiguous expressions:

```text
amount_expression = "42000+800 ins"
```

store:

```text
raw_expression = "42000+800 ins"
```

and ask Qwen to classify the components.

The Python layer must perform the arithmetic after classification.

For example, if Qwen returns:

```json
{
  "base_amount": 42000,
  "additional_amount": 800,
  "additional_type": "insurance",
  "included_in_selling_total": true
}
```

Python computes:

```text
selling_amount = 42800
```

Never ask Qwen to calculate the final accounting total without independently validating it.

---

# Phase 5 — Use Qwen3.5:4B Only for Fuzzy Interpretation

Use the local Ollama endpoint.

Default:

```text
http://localhost:11434
```

Model:

```text
qwen3.5:4b
```

Use temperature:

```text
0
```

Prefer structured JSON/schema output.

Ollama supports JSON Schema structured outputs; use that rather than hoping the model emits parseable JSON.

---

# Qwen Tasks

Qwen should be used for:

### 1. Name normalization

Example:

```text
"Mr. Muhammad Ali"
"Muhammad Ali"
"Muhd Ali"
"M Ali"
```

Return a candidate normalized representation.

BUT:

Do not merge records solely because Qwen says they look similar.

Use deterministic/fuzzy matching plus Qwen as supporting evidence.

---

### 2. Service normalization

Example:

```text
Visit Visa
Saudi Visa
Saudi visit visa
Visa Saudia
```

→

```text
category = Visa
```

---

### 3. Transaction interpretation

Example:

```text
42000+800 ins
```

Qwen should identify what the components appear to represent.

---

### 4. Ambiguous notes

Example:

```text
received zeeshan account
cash kamal
paid vendor
```

Classify the statement, but never treat it as proof of a payment unless the amount and transaction context support that conclusion.

---

### 5. Row classification

Classify each row as one of:

```text
SALE
PAYMENT
EXPENSE
SUPPLIER_PAYMENT
TRANSFER
NOTE
UNKNOWN
```

A row can be:

```text
SALE_WITH_PAYMENT
```

when it clearly contains both.

---

# Qwen JSON Schema

Use a strict schema similar to:

```json
{
  "type": "object",
  "properties": {
    "record_type": {
      "type": "string",
      "enum": [
        "SALE",
        "SALE_WITH_PAYMENT",
        "PAYMENT",
        "EXPENSE",
        "SUPPLIER_PAYMENT",
        "TRANSFER",
        "NOTE",
        "UNKNOWN"
      ]
    },
    "normalized_customer_name": {
      "type": ["string", "null"]
    },
    "normalized_supplier_name": {
      "type": ["string", "null"]
    },
    "canonical_service": {
      "type": ["string", "null"]
    },
    "subservice": {
      "type": ["string", "null"]
    },
    "amount_components": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "amount": {"type": "number"},
          "type": {"type": "string"},
          "description": {"type": "string"}
        },
        "required": [
          "amount",
          "type",
          "description"
        ]
      }
    },
    "payment_evidence": {
      "type": "string",
      "enum": [
        "explicit",
        "strong_context",
        "weak_context",
        "none"
      ]
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "review_required": {
      "type": "boolean"
    },
    "reason": {
      "type": "string"
    }
  },
  "required": [
    "record_type",
    "normalized_customer_name",
    "normalized_supplier_name",
    "canonical_service",
    "subservice",
    "amount_components",
    "payment_evidence",
    "confidence",
    "review_required",
    "reason"
  ],
  "additionalProperties": false
}
```

---

# IMPORTANT — Batch Qwen Requests

Do NOT make one huge request containing the whole workbook.

Process records in small batches.

Recommended:

```text
10–25 rows per request
```

depending on row size.

For normalization of repeated names/services, deduplicate the raw values first.

For example, if 124 transactions contain only 37 unique service labels:

```text
37 labels → Qwen
```

not:

```text
124 rows × Qwen
```

Likewise, normalize unique customer-name candidates before applying the mapping to transactions.

This will dramatically reduce local inference time.

---

# Phase 6 — Deterministic Validation

After Qwen returns a result, Python must validate it.

Reject/flag results when:

* schema validation fails
* confidence < threshold
* required fields are missing
* amount cannot be reconciled
* customer cannot be resolved
* service cannot be resolved
* source balance conflicts with calculated balance
* duplicate transaction is suspected
* payment has no defensible amount
* sale has impossible arithmetic

Never silently repair accounting data.

---

# Confidence Policy

Use:

```text
>= 0.90
HIGH
```

Eligible for automatic staging.

```text
0.70–0.89
MEDIUM
```

Stage but mark for review.

```text
< 0.70
LOW
```

Quarantine for manual review.

The confidence score must NOT come only from Qwen.

Calculate an overall confidence using deterministic signals too.

For example:

```text
overall_confidence =
    weighted(
        name_match,
        date_validity,
        service_match,
        amount_parse,
        transaction_type,
        qwen_confidence
    )
```

---

# Phase 7 — Party Deduplication

This is extremely important.

Do not create:

```text
Muhammad Ali
M. Ali
Muhd Ali
Muhammad  Ali
Mr Muhammad Ali
```

as five customers if they are clearly the same person.

But equally:

DO NOT automatically merge two people merely because their names are identical.

Create:

```text
party_master
party_alias
```

or equivalent mapping.

Example:

```text
raw_name → canonical_party_id
```

Every automatic merge must have a reason.

Potential matching signals:

1. exact normalized name
2. phone
3. email
4. country
5. repeated transaction pattern
6. Qwen semantic similarity

If ambiguity remains:

```text
review_required = true
```

---

# Phase 8 — Supplier Detection

Supplier/vendor data is particularly dirty.

Do not assume every value in a Vendor column is a supplier.

Potential values may actually be:

* dates
* notes
* staff names
* payment comments
* supplier names
* airline names
* hotel names

Classify supplier candidates.

Create:

```text
SupplierCandidate
```

with:

```text
raw_value
normalized_name
supplier_confidence
review_required
reason
```

Only promote to a real Odoo supplier after validation.

---

# Phase 9 — Payments

Payment import is high risk.

Only create a PaymentCandidate when there is sufficient evidence.

For each:

```text
PaymentCandidate
```

store:

* source_sheet
* source_row
* payment_date
* customer
* sale_reference
* amount
* payment_method
* collector
* raw_note
* evidence_level
* confidence
* review_required

Evidence levels:

```text
explicit
strong_context
weak_context
none
```

Only:

```text
explicit
```

should be automatically eligible for financial posting.

`strong_context` can be staged for review.

`weak_context` must NOT become an accounting payment automatically.

---

# Phase 10 — Expenses

Do NOT mix office expenses with sales.

Create a separate:

```text
ExpenseCandidate
```

Examples:

* office expenses
* salaries
* utilities
* miscellaneous expenses
* transport
* operational expenses

Expenses need their own accounting classification later.

Do not infer an accounting account from ambiguous text without explicit mapping rules.

---

# Phase 11 — Reconciliation Report

Before importing anything into Odoo, generate a reconciliation report.

At minimum:

```text
source row count
classified row count
SALE count
PAYMENT count
EXPENSE count
SUPPLIER_PAYMENT count
TRANSFER count
UNKNOWN count

source sales total
normalized sales total

source received total
normalized payment total

source remaining total
calculated remaining total

discrepancy count
review-required count
high-confidence count
medium-confidence count
low-confidence count
```

Also report:

```text
customer candidates
unique normalized customers
possible duplicate groups

raw services
canonical services

supplier candidates
suspected invalid suppliers
```

---

# Phase 12 — Odoo Import Must Be Separate

Do not couple classification with Odoo posting.

Implement:

```text
import classification
        ↓
staging database/files
        ↓
human review
        ↓
approved import
        ↓
Odoo
```

There must be a clear boundary.

A reviewer should be able to inspect:

```text
source row
→ classification
→ normalized customer
→ normalized service
→ amount
→ payment
→ confidence
→ reason
```

before approval.

---

# Import Rules

## Customers

Create only approved/validated parties.

## Services

Create canonical services once.

Preserve original source labels as aliases/subservices where useful.

## Sales

Create:

```text
Customer
Sale
Sale Line
Supplier Cost
```

where evidence supports them.

## Payments

Create only validated payments.

## Remaining

Never import source "Remaining" as authoritative.

Calculate:

```text
selling total - valid payments
```

inside Travel OS/Odoo.

---

# Golden Accounting Rule

For every imported sale:

```text
selling_total
- valid_customer_payments
= customer_outstanding
```

For every sale with a known supplier cost:

```text
selling_total
- supplier_cost
= gross_profit
```

Do not use Excel's manually calculated profit or remaining balance as authoritative.

---

# Required CLI

Implement a command such as:

```bash
python -m kamal_import inspect
```

Then:

```bash
python -m kamal_import classify
```

Then:

```bash
python -m kamal_import validate
```

Then:

```bash
python -m kamal_import report
```

And eventually:

```bash
python -m kamal_import import --approved
```

The default must NEVER post data to Odoo.

---

# Dry Run Requirement

The following must be possible:

```bash
python -m kamal_import classify --dry-run
```

and:

```bash
python -m kamal_import import --dry-run
```

Dry-run must make zero financial changes.

---

# Caching

Because Qwen is running locally and inference is relatively expensive:

Cache classification results.

For example:

```text
hash(raw_input + task_type + schema_version)
→ result
```

If the same service label appears 50 times, Qwen should not classify it 50 times.

Likewise for repeated names.

---

# Auditability

Every AI-derived result must retain:

```text
model_name
model_version
prompt_version
schema_version
input_hash
raw_input
structured_output
timestamp
confidence
```

This allows us to reproduce/debug the migration later.

---

# Testing

Create automated tests for:

### Classification

* Ticket
* Visa
* Hotel
* Insurance
* Appointment
* Umrah
* Hajj
* Apostille
* Case Preparation
* Other

### Name normalization

Test variations such as:

```text
Muhammad Ali
M. Ali
Mr. Muhammad Ali
Muhd Ali
```

### Amount parsing

Test:

```text
150000
150,000
18+9
42000+800 ins
```

### Balance

Given:

```text
sale = 150000
payment = 80000
```

must produce:

```text
outstanding = 70000
```

### Discrepancy

Given:

```text
sale = 150000
payment = 80000
source_remaining = 60000
```

must produce:

```text
calculated_remaining = 70000
discrepancy = 10000
review_required = true
```

### Ambiguous row

Must be quarantined rather than guessed.

### Duplicate detection

Must identify likely duplicate customers without blindly merging them.

---

# Acceptance Criteria

The implementation is complete only when:

* [ ] Entire Kamal workbook can be inspected programmatically.
* [ ] Every source row retains sheet + row lineage.
* [ ] Customers/parties can be extracted.
* [ ] Duplicate party candidates can be identified.
* [ ] Services can be normalized.
* [ ] Sales candidates can be extracted.
* [ ] Payments can be separately identified.
* [ ] Expenses are separated from sales.
* [ ] Supplier candidates are separated/validated.
* [ ] Qwen3.5:4B is used only where fuzzy interpretation is useful.
* [ ] Ollama structured output/schema validation is used.
* [ ] No financial arithmetic is delegated blindly to the LLM.
* [ ] Low-confidence records are quarantined.
* [ ] Source-vs-calculated discrepancies are reported.
* [ ] Classification is cached.
* [ ] Full reconciliation report is generated.
* [ ] No Odoo records are created during classification.
* [ ] Odoo import is an explicit later operation.
* [ ] Dry-run mode exists.
* [ ] Automated tests cover extraction, normalization and reconciliation.
* [ ] A human can inspect and approve ambiguous records before import.

---

# Final Deliverables

Produce:

```text
kamal_import/
    parser/
    classifiers/
    normalizers/
    validators/
    reconciliation/
    exporters/
    tests/
```

and generate:

```text
kamal_parties_staging.csv
kamal_services_staging.csv
kamal_sales_staging.csv
kamal_payments_staging.csv
kamal_expenses_staging.csv
kamal_suppliers_staging.csv
kamal_import_review.csv
kamal_reconciliation_report.html
```

Do not overwrite the original workbook.

---

# Most Important Instruction

The objective is NOT to make the LLM appear intelligent.

The objective is to produce **trustworthy, auditable migration data** from a messy historical spreadsheet.

Prefer:

```text
deterministic extraction
+
small Qwen classifications
+
strict schemas
+
validation
+
human review
```

over:

```text
large LLM prompt
+
guessed answers
+
automatic accounting import
```

If uncertain, preserve the raw value and flag it for review rather than inventing data.
