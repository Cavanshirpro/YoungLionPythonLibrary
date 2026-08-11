from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class Requester(DDM):
    id: int
    name: str
    tier: str
    country: str

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.name = str(data.get('name', ""))
        self.tier = str(data.get('tier', "free"))
        self.country = str(data.get('country', "Unknown"))


class Ticket(DDM):
    id: int
    subject: str
    status: str
    priority: int
    assigned: bool
    requester: Requester

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.subject = str(data.get('subject', ""))
        self.status = str(data.get('status', "open"))
        self.priority = int(data.get('priority', 1))
        self.assigned = bool(data.get('assigned', False))
        self.requester = Requester(data.get('requester', {}))

    def assign(self) -> None:
        if self.status == "closed": raise RuntimeError("closed ticket")
        self.assigned = True

    def close(self) -> None:
        self.status = "closed"
