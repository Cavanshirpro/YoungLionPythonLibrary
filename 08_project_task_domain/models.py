from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class Assignment(DDM):
    owner: str
    team: str
    blocked: bool

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.owner = str(data.get('owner', ""))
        self.team = str(data.get('team', ""))
        self.blocked = bool(data.get('blocked', False))


class Task(DDM):
    id: int
    title: str
    priority: int
    progress: float
    done: bool
    assignment: Assignment

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.title = str(data.get('title', ""))
        self.priority = int(data.get('priority', 1))
        self.progress = float(data.get('progress', 0.0))
        self.done = bool(data.get('done', False))
        self.assignment = Assignment(data.get('assignment', {}))

    def advance(self, delta: float) -> None:
        self.progress = min(1.0, max(0.0, self.progress + delta))
        self.done = self.progress >= 1.0

    def actionable(self) -> bool:
        return not self.done and not self.assignment.blocked
