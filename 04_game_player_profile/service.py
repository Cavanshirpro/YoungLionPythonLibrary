from __future__ import annotations
from repository import PlayerRepository


class PlayerService:
    def __init__(self, repository: PlayerRepository):
        self.repository = repository

    def demo(self):
        lions = self.repository.where(team="lion", level__ge=20)
        for p in lions:
            p.grant_xp(250)
        return [(p.name, round(p.win_rate, 3), p.xp) for p in lions]
