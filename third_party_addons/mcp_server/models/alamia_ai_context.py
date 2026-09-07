"""Alamia AI Employee Runtime — Context & Session Bootstrap.

Provides session context tracking and the `get_employee_profile` helper,
which bootstraps an authenticated Odoo user into an AI Assistant role profile.
"""

import logging
from .alamia_ai_registry import SKILLS, SkillRegistry

_logger = logging.getLogger(__name__)


class EmployeeContext:
    """Tracks active session context for an AI Employee."""

    def __init__(
        self,
        user_id,
        user_name,
        role_id,
        permissions=None,
        active_customer=None,
        active_booking=None,
        active_task=None,
        active_skill=None,
        pending_action=None,
        conversation_id=None,
    ):
        self.user_id = user_id
        self.user_name = user_name
        self.role_id = role_id
        self.permissions = permissions or {}
        self.active_customer = active_customer
        self.active_booking = active_booking
        self.active_task = active_task
        self.active_skill = active_skill
        self.pending_action = pending_action
        self.conversation_id = conversation_id

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "role_id": self.role_id,
            "permissions": self.permissions,
            "active_customer": self.active_customer,
            "active_booking": self.active_booking,
            "active_task": self.active_task,
            "active_skill": self.active_skill,
            "pending_action": self.pending_action,
            "conversation_id": self.conversation_id,
        }


def get_employee_role_id(user):
    """Determine the AI Assistant role ID based on Odoo user groups."""
    if user.has_group("alamia_travel_core.group_travel_ceo") or user.has_group("alamia_travel_core.group_travel_admin"):
        return "ceo_assistant"
    elif user.has_group("alamia_travel_core.group_travel_ops"):
        return "operations_assistant"
    elif user.has_group("account.group_account_user") or user.has_group("account.group_account_invoice"):
        return "accounting_assistant"
    elif user.has_group("alamia_travel_core.group_travel_sales"):
        return "sales_assistant"
    else:
        # Default operational assistant fallback for travel staff
        return "operations_assistant"


def resolve_allowed_tools_for_role(role_id):
    """Resolve the list of allowed MCP tools based on skills in the Role Manifest."""
    manifest = SkillRegistry.get_role_manifest(role_id)
    if not manifest:
        return ["get_employee_profile"]

    tools = set(["get_employee_profile"])
    for skill_id in manifest.skills:
        skill = SKILLS.get(skill_id)
        if skill:
            tools.update(skill.required_tools)

    # Always include basic action tools
    tools.update(["propose_action", "execute_action"])
    return sorted(list(tools))


def build_employee_profile_payload(env, user):
    """Build the complete session bootstrap payload for an authenticated user."""
    role_id = get_employee_role_id(user)
    manifest = SkillRegistry.get_role_manifest(role_id)
    allowed_skills = SkillRegistry.list_skills_for_role(role_id)
    allowed_tools = resolve_allowed_tools_for_role(role_id)

    context = EmployeeContext(
        user_id=user.id,
        user_name=user.name,
        role_id=role_id,
        permissions=manifest.permissions if manifest else {},
    )

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "login": user.login,
            "email": user.email or "",
        },
        "role_profile": manifest.to_dict() if manifest else {"id": role_id, "name": "Travel Assistant"},
        "allowed_skills": allowed_skills,
        "allowed_tools": allowed_tools,
        "session_context": context.to_dict(),
    }
