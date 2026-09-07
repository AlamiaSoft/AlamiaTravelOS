"""Alamia AI Employee Runtime — MCP Tool Adapter.

Contributes domain-aware Business Fact Tools and Action Tools to :class:`McpMixin`
via ``_inherit = 'mcp.mixin'``.

Categories:
1. Read / Fact Tools:
   - ``get_employee_profile``
   - ``get_customer_360``
   - ``get_booking_360``
   - ``get_work_items``
   - ``get_booking_profitability``
2. Action Tools:
   - ``propose_action``
   - ``execute_action``
   - ``create_followup``
"""

import json
import logging
from odoo import _, api, models
from odoo.exceptions import AccessError, MissingError, UserError

from .mcp_mixin import mcp_tool
from .mcp_tools_read import _tool_result
from .alamia_ai_context import build_employee_profile_payload, get_employee_role_id
from .alamia_ai_actions import (
    ACTION_DEFINITIONS,
    ActionProposal,
    ActionStateMachine,
)

_logger = logging.getLogger(__name__)


def _get_sale_customer(sale):
    return getattr(sale, "customer_id", getattr(sale, "partner_id", False))


def _get_sale_selling_amount(sale):
    return getattr(sale, "total_selling_amount", getattr(sale, "amount_total", 0.0))


def _get_sale_cost_amount(sale):
    return getattr(sale, "total_cost_amount", 0.0)


class McpToolsAlamiaAi(models.AbstractModel):
    _inherit = "mcp.mixin"

    # --- READ / FACT TOOLS ---

    @mcp_tool(
        name="get_employee_profile",
        title="Get Employee Profile & Session Bootstrap",
        description="Bootstrap the active session context, AI Assistant role profile, allowed skills, and tool catalog.",
        input_schema={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        operation="read",
        readOnlyHint=True,
    )
    @api.model
    def get_employee_profile(self, **params):
        """Return the complete session bootstrap payload for the current calling user."""
        user = self.env.user
        payload = build_employee_profile_payload(self.env, user)
        text = f"Alamia AI Profile for {user.name} ({payload['role_profile']['name']})"
        return _tool_result(text, payload)

    @mcp_tool(
        name="get_customer_360",
        title="Get Customer 360 Facts",
        description="Retrieve raw structured customer dossier: active bookings, lifetime spent, payment shortfall, and activities.",
        input_schema={
            "type": "object",
            "properties": {
                "partner_id": {"type": "integer", "description": "ID of the customer partner record."},
                "name": {"type": "string", "description": "Name search query if partner_id is not provided."},
            },
            "additionalProperties": False,
        },
        operation="read",
        readOnlyHint=True,
    )
    @api.model
    def get_customer_360(self, partner_id=None, name=None, **params):
        """Retrieve raw customer 360 facts."""
        Partner = self.env["res.partner"]
        partner = None

        if partner_id:
            partner = Partner.browse(partner_id)
        elif name:
            # 1. Search full name ilike
            partner = Partner.search([("name", "ilike", name)], limit=1)
            # 2. Token fallback search
            if not partner:
                for token in name.split():
                    if len(token) > 2:
                        partner = Partner.search([("name", "ilike", token)], limit=1)
                        if partner:
                            break

        if not partner or not partner.exists():
            sample_customers = Partner.search([("is_travel_customer", "=", True)], limit=5).mapped("name")
            sample_txt = f" Available customers include: {', '.join(sample_customers)}." if sample_customers else ""
            raise MissingError(_(f"Customer record '{name}' not found.{sample_txt}"))

        # Query bookings
        sales = self.env["travel.sale"].search([
            "|",
            ("customer_id", "=", partner.id),
            ("create_uid", "=", partner.id),
        ]) if hasattr(self.env["travel.sale"], "customer_id") else self.env["travel.sale"].search([])

        active_sales = sales.filtered(lambda s: s.state in ("draft", "confirmed", "in_progress"))
        completed_sales = sales.filtered(lambda s: s.state == "completed")

        total_spent = sum(_get_sale_selling_amount(s) for s in sales)
        total_unpaid = sum(getattr(s, "amount_residual", 0.0) for s in sales)

        # Query activities
        activities = self.env["mail.activity"].search([
            ("res_model", "=", "res.partner"),
            ("res_id", "=", partner.id),
        ])

        payload = {
            "customer": {
                "id": partner.id,
                "name": partner.name,
                "email": partner.email or "",
                "phone": partner.phone or partner.mobile or "",
                "whatsapp_number": getattr(partner, "whatsapp_number", False) or "",
                "cnic_passport": getattr(partner, "cnic_passport", False) or "",
            },
            "metrics": {
                "total_bookings_count": len(sales),
                "active_bookings_count": len(active_sales),
                "completed_bookings_count": len(completed_sales),
                "lifetime_spent": total_spent,
                "outstanding_unpaid_balance": total_unpaid,
            },
            "active_bookings": [
                {
                    "id": s.id,
                    "name": s.name,
                    "state": s.state,
                    "amount_total": _get_sale_selling_amount(s),
                    "create_date": str(s.create_date),
                }
                for s in active_sales
            ],
            "activities": [
                {
                    "id": a.id,
                    "summary": a.summary or "",
                    "activity_type": a.activity_type_id.name if a.activity_type_id else "",
                    "date_deadline": str(a.date_deadline),
                    "user_name": a.user_id.name if a.user_id else "",
                }
                for a in activities
            ],
        }

        text = f"Customer 360 dossier for {partner.name}: LTV PKR {total_spent:,.2f}, {len(active_sales)} active bookings."
        return _tool_result(text, payload)

    @mcp_tool(
        name="get_booking_360",
        title="Get Booking 360 Facts",
        description="Retrieve complete structured booking facts: passengers, service lines, payment shortfall, and tasks.",
        input_schema={
            "type": "object",
            "properties": {
                "booking_id": {"type": "integer", "description": "ID of the travel.sale record."},
                "name": {"type": "string", "description": "Sequence reference e.g. KE-2026-00001."},
            },
            "additionalProperties": False,
        },
        operation="read",
        readOnlyHint=True,
    )
    @api.model
    def get_booking_360(self, booking_id=None, name=None, **params):
        """Retrieve raw booking 360 facts."""
        Sale = self.env["travel.sale"]
        sale = None

        if booking_id:
            sale = Sale.browse(booking_id)
        elif name:
            sale = Sale.search([("name", "=", name)], limit=1)

        if not sale or not sale.exists():
            raise MissingError(_("Booking record not found."))

        customer = _get_sale_customer(sale)
        selling_total = _get_sale_selling_amount(sale)
        lines = getattr(sale, "line_ids", self.env["travel.sale.line"])
        passengers = getattr(sale, "passenger_ids", self.env["res.partner"])

        paid_amount = getattr(sale, "amount_paid", 0.0)
        residual_amount = getattr(sale, "amount_residual", selling_total - paid_amount)

        # Service lines breakdown
        service_lines = []
        for l in lines:
            service_lines.append({
                "id": l.id,
                "product_name": l.product_id.name if getattr(l, "product_id", False) else (getattr(l, "description", "Service Line")),
                "quantity": getattr(l, "quantity", getattr(l, "product_uom_qty", 1.0)),
                "price_unit": getattr(l, "selling_price", getattr(l, "price_unit", 0.0)),
                "selling_amount": getattr(l, "selling_amount", getattr(l, "price_subtotal", 0.0)),
                "cost_amount": getattr(l, "cost_amount", 0.0),
            })

        # Passenger details breakdown
        passenger_list = []
        for p in passengers:
            passenger_list.append({
                "id": p.id,
                "name": p.name,
                "cnic_passport": getattr(p, "cnic_passport", False) or "",
            })

        payload = {
            "booking": {
                "id": sale.id,
                "name": sale.name,
                "state": sale.state,
                "customer_id": customer.id if customer else False,
                "customer_name": customer.name if customer else "",
                "date_order": str(getattr(sale, "date_sale", sale.create_date)),
            },
            "financials": {
                "amount_total": selling_total,
                "amount_paid": paid_amount,
                "payment_shortfall": residual_amount,
                "is_paid": residual_amount <= 0.0,
            },
            "passengers": passenger_list,
            "services": service_lines,
        }

        cust_name = customer.name if customer else "N/A"
        text = f"Booking 360 for {sale.name} ({cust_name}): PKR {selling_total:,.2f} total, PKR {residual_amount:,.2f} shortfall."
        return _tool_result(text, payload)

    @mcp_tool(
        name="get_work_items",
        title="Get Work Items Facts",
        description="Retrieve raw operational work items (open activities, missing documents, unconfirmed services, payment shortfalls).",
        input_schema={
            "type": "object",
            "properties": {
                "urgency": {
                    "type": "string",
                    "enum": ["all", "critical", "attention", "routine"],
                    "description": "Urgency filter level.",
                },
            },
            "additionalProperties": False,
        },
        operation="read",
        readOnlyHint=True,
    )
    @api.model
    def get_work_items(self, urgency="all", **params):
        """Retrieve raw work items facts."""
        user = self.env.user
        domain = [("user_id", "=", user.id)]
        activities = self.env["mail.activity"].search(domain, order="date_deadline asc", limit=50)

        work_items = []
        today = self.env.cr.now().date() if hasattr(self.env.cr, "now") else None

        for a in activities:
            is_overdue = a.date_deadline and a.date_deadline < today if today else False
            item_urgency = "critical" if is_overdue else "attention"
            
            if urgency != "all" and urgency != item_urgency:
                continue

            work_items.append({
                "id": f"ACT-{a.id}",
                "activity_id": a.id,
                "type": a.activity_type_id.name if a.activity_type_id else "task",
                "summary": a.summary or "Activity Follow-up",
                "res_model": a.res_model,
                "res_id": a.res_id,
                "deadline": str(a.date_deadline),
                "is_overdue": is_overdue,
                "urgency": item_urgency,
                "owner": a.user_id.name,
            })

        payload = {
            "user_id": user.id,
            "total_items": len(work_items),
            "urgency_filter": urgency,
            "items": work_items,
        }

        text = f"Found {len(work_items)} work items for {user.name}."
        return _tool_result(text, payload)

    @mcp_tool(
        name="get_booking_profitability",
        title="Get Booking Profitability Facts",
        description="Perform deterministic financial calculation of revenue, supplier cost lines, commissions, gross profit, and margin %.",
        input_schema={
            "type": "object",
            "properties": {
                "booking_id": {"type": "integer", "description": "ID of the travel.sale record."},
                "name": {"type": "string", "description": "Sequence reference e.g. KE-2026-00001."},
            },
            "additionalProperties": False,
        },
        operation="read",
        readOnlyHint=True,
    )
    @api.model
    def get_booking_profitability(self, booking_id=None, name=None, **params):
        """Retrieve deterministic booking profitability facts."""
        Sale = self.env["travel.sale"]
        sale = None

        if booking_id:
            sale = Sale.browse(booking_id)
        elif name:
            sale = Sale.search([("name", "=", name)], limit=1)

        if not sale or not sale.exists():
            raise MissingError(_("Booking record not found."))

        customer = _get_sale_customer(sale)
        revenue = _get_sale_selling_amount(sale)
        cost_total = _get_sale_cost_amount(sale)
        gross_profit = getattr(sale, "gross_profit", revenue - cost_total)
        lines = getattr(sale, "line_ids", self.env["travel.sale.line"])

        cost_breakdown = []
        for l in lines:
            sell_amt = getattr(l, "selling_amount", getattr(l, "price_subtotal", 0.0))
            cost_amt = getattr(l, "cost_amount", 0.0)
            cost_breakdown.append({
                "line_id": l.id,
                "service": l.product_id.name if getattr(l, "product_id", False) else getattr(l, "description", "Line"),
                "selling_amount": sell_amt,
                "cost_amount": cost_amt,
                "margin": sell_amt - cost_amt,
            })

        margin_pct = (gross_profit / revenue * 100.0) if revenue > 0 else 0.0

        payload = {
            "booking": {
                "id": sale.id,
                "name": sale.name,
                "customer": customer.name if customer else "",
            },
            "profitability": {
                "revenue": revenue,
                "total_supplier_cost": cost_total,
                "gross_profit": gross_profit,
                "margin_percentage": round(margin_pct, 2),
                "is_profitable": gross_profit >= 0,
            },
            "cost_lines": cost_breakdown,
        }

        text = f"Profitability for {sale.name}: Revenue PKR {revenue:,.2f}, Cost PKR {cost_total:,.2f}, Profit PKR {gross_profit:,.2f} ({margin_pct:.1f}% margin)."
        return _tool_result(text, payload)

    # --- ACTION TOOLS ---

    @mcp_tool(
        name="propose_action",
        title="Propose Action Mutation",
        description="Generate a validated ActionProposal JSON structure against backend-registered ActionDefinitions.",
        input_schema={
            "type": "object",
            "properties": {
                "action_type": {"type": "string", "description": "Registered action type e.g. create_followup, update_booking_status."},
                "target": {"type": "object", "description": "Target record metadata {'model': ..., 'id': ...}."},
                "reason": {"type": "string", "description": "Business intent/reason for proposing this action."},
                "proposed_changes": {"type": "object", "description": "Field modifications or parameters."},
                "idempotency_key": {"type": "string", "description": "Unique key to ensure single execution."},
            },
            "required": ["action_type", "reason"],
            "additionalProperties": False,
        },
        operation=None,
    )
    @api.model
    def propose_action(self, action_type, reason, target=None, proposed_changes=None, idempotency_key=None, **params):
        """Propose an action mutation."""
        user = self.env.user
        role_id = get_employee_role_id(user)

        # Validate authorization against backend definition
        ActionStateMachine.validate_action_authorization(user, role_id, action_type)

        proposal = ActionProposal(
            action_type=action_type,
            target=target or {},
            reason=reason,
            proposed_changes=proposed_changes or {},
            idempotency_key=idempotency_key,
            created_by=user.name,
        )

        ActionStateMachine.register_proposal(proposal)
        payload = proposal.to_dict()
        text = f"Action proposed: {proposal.action_id} ({action_type}) - Status: {proposal.status}"
        return _tool_result(text, payload)

    @mcp_tool(
        name="create_followup",
        title="Create Activity & Log Chatter Audit",
        description="Schedule a follow-up activity on a record and post a chatter audit trail entry.",
        input_schema={
            "type": "object",
            "properties": {
                "res_model": {"type": "string", "description": "Target model e.g. res.partner, travel.sale."},
                "res_id": {"type": "integer", "description": "Target record ID."},
                "summary": {"type": "string", "description": "Activity summary/title."},
                "note": {"type": "string", "description": "Activity body notes."},
                "date_deadline": {"type": "string", "description": "Due date (YYYY-MM-DD)."},
                "idempotency_key": {"type": "string", "description": "Idempotency key."},
            },
            "required": ["res_model", "res_id", "summary"],
            "additionalProperties": False,
        },
        operation="write",
    )
    @api.model
    def create_followup(self, res_model, res_id, summary, note=None, date_deadline=None, idempotency_key=None, **params):
        """Create mail.activity and post chatter audit trail note."""
        user = self.env.user
        role_id = get_employee_role_id(user)

        # Check authorization
        ActionStateMachine.validate_action_authorization(user, role_id, "create_followup")

        # Idempotency check
        if idempotency_key and ActionStateMachine.is_idempotency_executed(idempotency_key):
            existing_payload = ActionStateMachine.get_executed_payload(idempotency_key)
            return _tool_result("Idempotency key previously executed.", existing_payload)

        # Target record check
        record = self.env[res_model].browse(res_id)
        if not record.exists():
            raise MissingError(_(f"Target record {res_model},{res_id} does not exist."))

        # Create activity
        act_type = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        model_id = self.env["ir.model"]._get_id(res_model)
        activity = self.env["mail.activity"].sudo().create({
            "res_model": res_model,
            "res_model_id": model_id,
            "res_id": res_id,
            "activity_type_id": act_type.id if act_type else 1,
            "summary": summary,
            "note": note or "",
            "date_deadline": date_deadline or self.env.cr.now().date(),
            "user_id": user.id,
        })

        # Post chatter audit log entry
        chatter_msg = (
            f"🤖 <b>Alamia AI Audit Trail</b><br/>"
            f"Action: Scheduled Follow-up Activity<br/>"
            f"Executed by: {user.name} ({role_id})<br/>"
            f"Summary: {summary}"
        )
        if hasattr(record, "message_post"):
            record.message_post(body=chatter_msg)

        payload = {
            "activity_id": activity.id,
            "res_model": res_model,
            "res_id": res_id,
            "summary": summary,
            "date_deadline": str(activity.date_deadline),
            "status": "COMPLETED",
        }

        # Register proposal & mark executed in state machine for idempotency tracking
        proposal = ActionProposal(
            action_type="create_followup",
            target={"model": res_model, "id": res_id},
            reason=summary,
            idempotency_key=idempotency_key,
            created_by=user.name,
        )
        ActionStateMachine.mark_executed(proposal, payload)

        text = f"Follow-up activity scheduled for {record.display_name}: '{summary}'."
        return _tool_result(text, payload)
