This is now **good enough to lock and implement**.

I would make only a few **implementation-level corrections**, not another architecture revision.

### What I would lock

Your four boundaries are exactly right:

```text
Business Tool
    = facts

Skill
    = reasoning / business workflow

ActionProposal
    = intended mutation

Tool Adapter
    = authorized execution
```

That is the key architectural achievement here.

### One important correction

The `mcp_tools_alamia_ai.py` description says:

> MCP Tool Adapter for deterministic facts tools

but it also contains:

* `propose_action`
* `execute_action`
* `create_followup`

Those aren't deterministic **facts** tools. I'd document the adapter as having two categories:

```text
MCP Tool Adapter
├── Read / Fact Tools
│   ├── get_employee_profile
│   ├── get_customer_360
│   ├── get_booking_360
│   ├── get_work_items
│   └── get_booking_profitability
│
└── Action Tools
    ├── propose_action
    ├── execute_action
    └── create_followup
```

This distinction will matter enormously when you later add more write operations.

### One security rule I'd explicitly add

**Never trust `role`, `permissions`, `risk_level`, or `requires_confirmation` supplied by the model.**

The backend must derive/enforce these.

For example, the model cannot say:

```json
{
  "action_type": "post_invoice",
  "risk_level": "low",
  "requires_confirmation": false
}
```

and thereby bypass controls.

Instead:

```text
LLM proposes intent
        ↓
Backend resolves action definition
        ↓
Backend checks:
  identity
  role
  permission
  target
  risk
  confirmation policy
  idempotency
        ↓
execute / deny
```

That's a **hard security boundary**, not an LLM instruction.

### I would also add one field

For `ActionProposal`:

```text
action_definition
```

or

```text
action_type
```

must resolve to a **registered backend action definition**, rather than arbitrary model-generated operations.

Conceptually:

```text
ActionDefinition
├── id
├── description
├── required_permission
├── risk_level
├── confirmation_policy
├── allowed_roles
├── executor
└── version
```

Then:

```text
Skill
  ↓
ActionProposal
  ↓
ActionDefinition lookup
  ↓
Authorization
  ↓
Confirmation Policy
  ↓
Idempotency
  ↓
Executor
  ↓
MCP
```

That makes the action system extensible without turning it into an unsafe generic "AI can execute anything" interface.

---

## One thing I would *not* implement yet

Don't build the full proactive event engine, memory persistence, STT/TTS, WhatsApp adapter, etc. in this sprint.

Create their **interfaces/contracts**, as you've done with `EmployeeEvent`, but keep the implementation minimal.

The first milestone should prove:

> **An authenticated employee can enter TravelOS AI, receive only their permitted capabilities, ask a business question, get deterministic facts, have an AI skill reason over them, propose a safe action, confirm it, execute it exactly once, and produce an audit trail.**

If that works, you have the foundation.

If it doesn't, adding voice/events/memory will only hide the architectural problems.

### Recommended implementation order

```text
1. Registry
      ↓
2. EmployeeContext / identity
      ↓
3. Business fact tools
      ↓
4. ActionDefinition
      ↓
5. ActionProposal + state machine
      ↓
6. Authorization + confirmation + idempotency
      ↓
7. First 2–3 skills
      ↓
8. MCP adapter execution
      ↓
9. Audit
      ↓
10. Behavioral/security tests
```

Then add:

```text
11. Remaining skills
12. Proactive events
13. Memory
14. Voice/STT/TTS
15. WhatsApp/Web/API adapters
```

### Final verdict

**Architecture: LOCKED.**

I would not spend another round redesigning it.

The next artifact should be an **implementation prompt for OpenCode/Qwen** that tells the coding agent to implement this incrementally, inspect the existing MCP/Odoo architecture first, reuse existing models/tools wherever possible, and **not invent parallel Odoo models or duplicate existing functionality**.

That last point is particularly important for this project: the agent should extend the existing MCP server and TravelOS domain rather than accidentally creating a second "AI version" of customers, bookings, payments, or tasks.
