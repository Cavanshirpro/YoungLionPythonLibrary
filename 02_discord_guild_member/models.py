from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class ModerationState(DDM):
    warnings: int
    muted: bool
    reason: str

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.warnings = int(data.get('warnings', 0))
        self.muted = bool(data.get('muted', False))
        self.reason = str(data.get('reason', ""))


class GuildMember(DDM):
    id: int
    name: str
    level: int
    balance: float
    online: bool
    moderation: ModerationState

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.name = str(data.get('name', "Unknown"))
        self.level = int(data.get('level', 0))
        self.balance = float(data.get('balance', 0.0))
        self.online = bool(data.get('online', False))
        self.moderation = ModerationState(data.get('moderation', {}))

    def reward(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("reward cannot be negative")
        self.balance += amount

    def needs_moderator(self) -> bool:
        return self.moderation.muted or self.moderation.warnings >= 3
