from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class Actor(DDM):
    id: int
    name: str
    ip: str
    country: str

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.name = str(data.get('name', ""))
        self.ip = str(data.get('ip', ""))
        self.country = str(data.get('country', ""))


class AuditEvent(DDM):
    id: int
    event_type: str
    severity: int
    resource: str
    success: bool
    actor: Actor

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.event_type = str(data.get('event_type', ""))
        self.severity = int(data.get('severity', 0))
        self.resource = str(data.get('resource', ""))
        self.success = bool(data.get('success', False))
        self.actor = Actor(data.get('actor', {}))

    def security_relevant(self) -> bool:
        return self.severity >= 4 or not self.success

    def summary(self) -> str:
        return f"{self.event_type} by {self.actor.name} on {self.resource}"
