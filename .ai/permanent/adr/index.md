# Architecture Decision Records — Index

## Purpose
This directory contains Architecture Decision Records (ADRs) that document significant design decisions made during the AlamiaTravelOS project. Each ADR captures:
- The context and problem faced
- Considered options
- Decision and rationale
- Status (proposed, accepted, deprecated, superseded)

## How to Use
- Read ADRs before making similar design choices
- Reference ADRs in code comments and PR descriptions
- Deprecate old decisions when superseded by better approaches
- Maintain chronological order; new ADRs appended at end

## ADR List (chronological order)

| ADR ID | Title | Status | Related File |
|--------|-------|--------|--------------|
| ADR-001 | Named Volumes for Production Compose | Accepted | `docker-compose.prod.yml` (lines 66-80) |
| ADR-002 | Incremental Data Migration via Task Docs | Accepted | `docs/kamal-express/data-import/` |
| ADR-003 | MCP Server for External Tool Auth | Proposed | `third_party_addons/mcp_server/` |
| ... | ... | ... | ... |