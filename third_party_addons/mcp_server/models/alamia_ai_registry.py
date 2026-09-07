"""Alamia AI Employee Runtime — Skill Registry & Role Manifests.

Defines the generic AI Employee Runtime abstractions:
- SkillDefinition: Structured contracts for reusable business skills.
- RoleManifest: Structured AI Assistant profiles for CEO, Operations, Sales, Accounting, and Ticketing.
- SkillRegistry: Centralized registry lookup for skills and role manifests.
"""

import logging

_logger = logging.getLogger(__name__)


class SkillDefinition:
    """Represents an executable business skill definition in Alamia AI."""

    def __init__(
        self,
        skill_id,
        name,
        description,
        objectives,
        required_tools,
        input_schema=None,
        output_schema=None,
        risk_level="read",
        allowed_roles=None,
        version="1.0",
    ):
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.objectives = objectives or []
        self.required_tools = required_tools or []
        self.input_schema = input_schema or {}
        self.output_schema = output_schema or {}
        self.risk_level = risk_level
        self.allowed_roles = allowed_roles or []
        self.version = version

    def to_dict(self):
        return {
            "id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "objectives": self.objectives,
            "required_tools": self.required_tools,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "risk_level": self.risk_level,
            "allowed_roles": self.allowed_roles,
            "version": self.version,
        }


class RoleManifest:
    """Represents an AI Assistant role profile in Alamia AI."""

    def __init__(
        self,
        role_id,
        name,
        objectives,
        skills,
        permissions=None,
        proactive_rules=None,
        escalation_policy=None,
        configuration=None,
    ):
        self.role_id = role_id
        self.name = name
        self.objectives = objectives or []
        self.skills = skills or []
        self.permissions = permissions or {"read": [], "write": [], "approval_required": []}
        self.proactive_rules = proactive_rules or []
        self.escalation_policy = escalation_policy or {}
        self.configuration = configuration or {}

    def to_dict(self):
        return {
            "id": self.role_id,
            "name": self.name,
            "objectives": self.objectives,
            "skills": self.skills,
            "permissions": self.permissions,
            "proactive_rules": self.proactive_rules,
            "escalation_policy": self.escalation_policy,
            "configuration": self.configuration,
        }


# --- SKILL DEFINITIONS REGISTRY ---

SKILLS = {
    "customer_360": SkillDefinition(
        skill_id="customer_360",
        name="Customer 360",
        description="Retrieve complete customer dossier, lifetime value, active bookings, payment status, and document completeness.",
        objectives=["Analyze customer relationship", "Identify active bookings", "Check outstanding payment balances"],
        required_tools=["get_customer_360"],
        risk_level="read",
        allowed_roles=["ceo_assistant", "operations_assistant", "sales_assistant", "accounting_assistant"],
    ),
    "booking_360": SkillDefinition(
        skill_id="booking_360",
        name="Booking 360",
        description="Retrieve comprehensive booking status, passenger breakdown, visa states, supplier service allocations, and payment shortfalls.",
        objectives=["Inspect booking details", "Check passenger document & visa readiness", "Analyze supplier confirmations"],
        required_tools=["get_booking_360"],
        risk_level="read",
        allowed_roles=["ceo_assistant", "operations_assistant", "sales_assistant", "ticketing_assistant"],
    ),
    "booking_readiness": SkillDefinition(
        skill_id="booking_readiness",
        name="Booking Departure Readiness",
        description="Analyze departure readiness, missing passport/visa documents, and unconfirmed supplier services for upcoming trips.",
        objectives=["Identify operational blockers", "Detect missing passenger visas", "Verify supplier flight and hotel allocations"],
        required_tools=["get_booking_360", "get_work_items"],
        risk_level="read",
        allowed_roles=["operations_assistant", "ticketing_assistant", "ceo_assistant"],
    ),
    "daily_briefing": SkillDefinition(
        skill_id="daily_briefing",
        name="Daily Employee Briefing",
        description="Provide a role-scoped morning work briefing summarizing critical operational items, overdues, and priorities.",
        objectives=["Summarize daily priorities", "Highlight critical overdues", "Organize role work queue"],
        required_tools=["get_work_items"],
        risk_level="read",
        allowed_roles=["ceo_assistant", "operations_assistant", "sales_assistant", "accounting_assistant", "ticketing_assistant"],
    ),
    "payment_followup": SkillDefinition(
        skill_id="payment_followup",
        name="Payment Follow-up & Receivables",
        description="Analyze payment shortfalls and propose payment follow-up activities with chatter audit logging.",
        objectives=["Identify overdue receivables", "Propose follow-up activities for sales/accounts"],
        required_tools=["get_work_items", "propose_action", "create_followup"],
        risk_level="write",
        allowed_roles=["sales_assistant", "accounting_assistant", "ceo_assistant"],
    ),
    "booking_profitability": SkillDefinition(
        skill_id="booking_profitability",
        name="Booking Profitability Analysis",
        description="Perform deterministic financial calculation of revenue, supplier costs, agent commissions, and net margin %.",
        objectives=["Calculate gross margin %", "Itemize supplier cost lines", "Detect margin shrinkage"],
        required_tools=["get_booking_profitability"],
        risk_level="read",
        allowed_roles=["ceo_assistant", "accounting_assistant"],
    ),
    "work_queue": SkillDefinition(
        skill_id="work_queue",
        name="Operational Work Queue",
        description="Retrieve and filter raw work items by urgency (critical, attention, routine) for the active employee.",
        objectives=["Filter open activities", "Highlight urgent tasks"],
        required_tools=["get_work_items"],
        risk_level="read",
        allowed_roles=["ceo_assistant", "operations_assistant", "sales_assistant", "accounting_assistant", "ticketing_assistant"],
    ),
}

# --- ROLE MANIFESTS REGISTRY ---

ROLE_MANIFESTS = {
    "ceo_assistant": RoleManifest(
        role_id="ceo_assistant",
        name="CEO Executive Assistant",
        objectives=[
            "Executive oversight over sales, operational risks, and financial profitability.",
            "Monitor company-wide cash positions, receivables, and gross margin trends.",
            "Receive daily executive briefings and critical risk alerts.",
        ],
        skills=["daily_briefing", "customer_360", "booking_360", "booking_profitability", "work_queue", "booking_readiness"],
        permissions={
            "read": ["travel.sale", "res.partner", "account.move", "mail.activity"],
            "write": ["mail.activity"],
            "approval_required": ["post_invoice", "register_payment", "booking_cancellation"],
        },
        proactive_rules=["executive_briefing", "margin_alert", "overdue_receivables_alert"],
    ),
    "operations_assistant": RoleManifest(
        role_id="operations_assistant",
        name="Operations Assistant",
        objectives=[
            "Ensure all confirmed bookings are operationally ready before departure.",
            "Verify passenger passport uploads, visa applications, and document completeness.",
            "Coordinate flight, hotel, and transport allocations with suppliers.",
        ],
        skills=["daily_briefing", "booking_readiness", "booking_360", "customer_360", "work_queue", "payment_followup"],
        permissions={
            "read": ["travel.sale", "res.partner", "travel.service.catalog", "mail.activity"],
            "write": ["mail.activity", "travel.sale"],
            "approval_required": ["booking_cancellation", "price_change"],
        },
        proactive_rules=["departure_48h_alert", "visa_missing_alert", "supplier_unconfirmed_alert"],
    ),
    "sales_assistant": RoleManifest(
        role_id="sales_assistant",
        name="Sales Assistant",
        objectives=[
            "Maintain customer relationships and provide Customer 360 dossiers.",
            "Track sales pipeline, follow up on quotations, and resolve payment shortfalls.",
            "Schedule customer follow-ups and log chatter audit notes.",
        ],
        skills=["daily_briefing", "customer_360", "booking_360", "payment_followup", "work_queue"],
        permissions={
            "read": ["travel.sale", "res.partner", "travel.service.catalog", "mail.activity"],
            "write": ["mail.activity", "travel.sale"],
            "approval_required": ["discount_override", "booking_cancellation"],
        },
        proactive_rules=["quotation_followup_alert", "payment_shortfall_alert"],
    ),
    "accounting_assistant": RoleManifest(
        role_id="accounting_assistant",
        name="Accounting Assistant",
        objectives=[
            "Monitor customer receivables, aging balances, and outstanding invoices.",
            "Analyze booking profitability, supplier costs, and agent commissions.",
            "Prepare daily close briefings and audit payment proposals.",
        ],
        skills=["daily_briefing", "booking_profitability", "payment_followup", "customer_360", "work_queue"],
        permissions={
            "read": ["account.move", "travel.sale", "res.partner", "mail.activity"],
            "write": ["mail.activity"],
            "approval_required": ["post_invoice", "register_payment", "refund_issue"],
        },
        proactive_rules=["receivables_overdue_alert", "daily_close_briefing"],
    ),
    "ticketing_assistant": RoleManifest(
        role_id="ticketing_assistant",
        name="Ticketing Assistant",
        objectives=[
            "Monitor PNR statuses, flight schedules, ticket issuances, and reissues.",
            "Ensure passenger details match passport data for flight bookings.",
            "Identify unconfirmed flight allocations for upcoming departures.",
        ],
        skills=["daily_briefing", "booking_readiness", "booking_360", "work_queue"],
        permissions={
            "read": ["travel.sale", "res.partner", "mail.activity"],
            "write": ["mail.activity"],
            "approval_required": ["ticket_reissue_cost"],
        },
        proactive_rules=["departure_flight_alert", "pnr_unconfirmed_alert"],
    ),
}


class SkillRegistry:
    """Helper class to query skills and role manifests."""

    @classmethod
    def get_skill(cls, skill_id):
        return SKILLS.get(skill_id)

    @classmethod
    def get_role_manifest(cls, role_id):
        return ROLE_MANIFESTS.get(role_id)

    @classmethod
    def list_skills_for_role(cls, role_id):
        manifest = cls.get_role_manifest(role_id)
        if not manifest:
            return []
        return [SKILLS[sid].to_dict() for sid in manifest.skills if sid in SKILLS]
