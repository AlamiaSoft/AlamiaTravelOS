"""Alamia AI Employee Runtime — Action Definitions, Proposals & State Machine.

Implements the first-class `ActionProposal` abstraction, backend-registered
`ActionDefinition` catalog, and `ActionStateMachine` enforcing hard backend-derived
access controls, risk levels, confirmation policies, idempotency keys, and chatter auditing.
"""

import datetime
import uuid
import logging
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)


class ActionDefinition:
    """Registered backend action definition."""

    def __init__(
        self,
        action_type,
        description,
        required_permission,
        risk_level="read",
        confirmation_policy="none",
        allowed_roles=None,
        version="1.0",
    ):
        self.action_type = action_type
        self.description = description
        self.required_permission = required_permission
        self.risk_level = risk_level  # read, low_risk_write, operational_write, financial_write
        self.confirmation_policy = confirmation_policy  # none, required, authorization_required
        self.allowed_roles = allowed_roles or []
        self.version = version

    def to_dict(self):
        return {
            "action_type": self.action_type,
            "description": self.description,
            "required_permission": self.required_permission,
            "risk_level": self.risk_level,
            "confirmation_policy": self.confirmation_policy,
            "allowed_roles": self.allowed_roles,
            "version": self.version,
        }


# --- REGISTERED ACTION DEFINITIONS CATALOG ---

ACTION_DEFINITIONS = {
    "create_followup": ActionDefinition(
        action_type="create_followup",
        description="Schedule a follow-up activity on a record and post a chatter audit trail note.",
        required_permission="mail.activity.create",
        risk_level="low_risk_write",
        confirmation_policy="none",
        allowed_roles=["ceo_assistant", "operations_assistant", "sales_assistant", "accounting_assistant", "ticketing_assistant"],
    ),
    "update_booking_status": ActionDefinition(
        action_type="update_booking_status",
        description="Update state or stage on a booking record.",
        required_permission="travel.sale.write",
        risk_level="operational_write",
        confirmation_policy="required",
        allowed_roles=["operations_assistant", "sales_assistant", "ceo_assistant"],
    ),
    "post_invoice": ActionDefinition(
        action_type="post_invoice",
        description="Post a draft invoice into accounting.",
        required_permission="account.group_account_invoice",
        risk_level="financial_write",
        confirmation_policy="authorization_required",
        allowed_roles=["accounting_assistant", "ceo_assistant"],
    ),
    "register_payment": ActionDefinition(
        action_type="register_payment",
        description="Register a payment against a customer invoice.",
        required_permission="account.group_account_user",
        risk_level="financial_write",
        confirmation_policy="authorization_required",
        allowed_roles=["accounting_assistant", "ceo_assistant"],
    ),
}


class ActionProposal:
    """First-class representation of an intended record mutation."""

    VALID_STATES = [
        "PROPOSED",
        "AWAITING_CONFIRMATION",
        "CONFIRMED",
        "EXECUTING",
        "COMPLETED",
        "REJECTED",
        "EXPIRED",
        "FAILED",
    ]

    def __init__(
        self,
        action_type,
        target,
        reason,
        proposed_changes=None,
        idempotency_key=None,
        created_by=None,
        action_id=None,
    ):
        definition = ACTION_DEFINITIONS.get(action_type)
        if not definition:
            raise UserError(f"Unknown or unregistered action type: '{action_type}'")

        self.action_id = action_id or f"ACT-{uuid.uuid4().hex[:8].upper()}"
        self.idempotency_key = idempotency_key or f"IDEMP-{uuid.uuid4().hex[:12]}"
        self.action_type = action_type
        self.target = target or {}
        self.reason = reason
        self.proposed_changes = proposed_changes or {}
        self.created_by = created_by or "system"
        self.created_at = datetime.datetime.utcnow().isoformat()

        # HARD BACKEND-DERIVED SECURITY: Values come strictly from backend definition!
        self.risk_level = definition.risk_level
        self.requires_confirmation = definition.confirmation_policy != "none"
        self.required_permission = definition.required_permission
        self.allowed_roles = definition.allowed_roles

        self.status = "AWAITING_CONFIRMATION" if self.requires_confirmation else "PROPOSED"

    def to_dict(self):
        return {
            "action_id": self.action_id,
            "idempotency_key": self.idempotency_key,
            "action_type": self.action_type,
            "target": self.target,
            "reason": self.reason,
            "proposed_changes": self.proposed_changes,
            "risk_level": self.risk_level,
            "requires_confirmation": self.requires_confirmation,
            "required_permission": self.required_permission,
            "allowed_roles": self.allowed_roles,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "status": self.status,
        }


# --- IN-MEMORY ACTION PROPOSAL & IDEMPOTENCY CACHE ---

_ACTION_PROPOSALS = {}
_EXECUTED_IDEMPOTENCY_KEYS = {}


class ActionStateMachine:
    """Manages ActionProposal lifecycles and idempotency checks."""

    @classmethod
    def register_proposal(cls, proposal):
        if proposal.idempotency_key in _EXECUTED_IDEMPOTENCY_KEYS:
            existing = _EXECUTED_IDEMPOTENCY_KEYS[proposal.idempotency_key]
            _logger.info("Idempotency key %s previously executed.", proposal.idempotency_key)
            return existing

        _ACTION_PROPOSALS[proposal.action_id] = proposal
        return proposal

    @classmethod
    def get_proposal(cls, action_id):
        return _ACTION_PROPOSALS.get(action_id)

    @classmethod
    def get_executed_payload(cls, idempotency_key):
        return _EXECUTED_IDEMPOTENCY_KEYS.get(idempotency_key)

    @classmethod
    def is_idempotency_executed(cls, idempotency_key):
        return idempotency_key in _EXECUTED_IDEMPOTENCY_KEYS

    @classmethod
    def mark_executed(cls, proposal, result_payload):
        proposal.status = "COMPLETED"
        _EXECUTED_IDEMPOTENCY_KEYS[proposal.idempotency_key] = {
            "proposal": proposal.to_dict(),
            "result": result_payload,
            "executed_at": datetime.datetime.utcnow().isoformat(),
        }

    @classmethod
    def mark_failed(cls, proposal, error_msg):
        proposal.status = "FAILED"

    @classmethod
    def validate_action_authorization(cls, user, role_id, action_type):
        """Backend authorization check enforcing role allowed list and user permissions."""
        definition = ACTION_DEFINITIONS.get(action_type)
        if not definition:
            raise UserError(f"Action definition '{action_type}' is not registered.")

        # Check role allowed list
        if role_id not in definition.allowed_roles:
            raise AccessError(
                f"Role '{role_id}' is not authorized to execute action '{action_type}'."
            )

        # Check Odoo security permissions
        if definition.required_permission == "account.group_account_invoice":
            if not (user.has_group("account.group_account_invoice") or user.has_group("account.group_account_user")):
                raise AccessError(f"User '{user.name}' lacks accounting invoice permission for '{action_type}'.")
        elif definition.required_permission == "account.group_account_user":
            if not user.has_group("account.group_account_user"):
                raise AccessError(f"User '{user.name}' lacks financial user permission for '{action_type}'.")

        return True
