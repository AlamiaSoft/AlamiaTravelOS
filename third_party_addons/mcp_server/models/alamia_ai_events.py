"""Alamia AI Employee Runtime — Proactive Event Contract.

Defines the `EmployeeEvent` schema for proactive notifications and trigger alerts.
"""

from datetime import datetime


class EmployeeEvent:
    """Represents a proactive system event emitted for AI Employees."""

    def __init__(
        self,
        event_type,
        source_model,
        record_id,
        severity="medium",
        affected_roles=None,
        payload=None,
        timestamp=None,
    ):
        self.event_type = event_type
        self.source_model = source_model
        self.record_id = record_id
        self.severity = severity
        self.affected_roles = affected_roles or []
        self.payload = payload or {}
        self.timestamp = timestamp or datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "event_type": self.event_type,
            "source_model": self.source_model,
            "record_id": self.record_id,
            "severity": self.severity,
            "affected_roles": self.affected_roles,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }
