from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class CombatStats(DDM):
    wins: int
    losses: int
    damage: float

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.wins = int(data.get('wins', 0))
        self.losses = int(data.get('losses', 0))
        self.damage = float(data.get('damage', 0.0))


class Player(DDM):
    id: int
    name: str
    level: int
    xp: float
    team: str
    stats: CombatStats

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.name = str(data.get('name', "Player"))
        self.level = int(data.get('level', 1))
        self.xp = float(data.get('xp', 0.0))
        self.team = str(data.get('team', "solo"))
        self.stats = CombatStats(data.get('stats', {}))

    @property
    def win_rate(self) -> float:
        games = self.stats.wins + self.stats.losses
        return self.stats.wins / games if games else 0.0

    def grant_xp(self, amount: float) -> None:
        self.xp += max(0.0, amount)
