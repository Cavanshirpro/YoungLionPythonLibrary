from __future__ import annotations
from repository import GuildMemberRepository


class GuildMemberService:
    def __init__(self, repository: GuildMemberRepository):
        self.repository = repository

    def demo(self):
        risky = self.repository.where(moderation__warnings__ge=2)
        online = self.repository.where(online=True)
        for member in online:
            member.reward(25)
        return {"needs_review": [m.name for m in risky], "online_balances": {m.name: m.balance for m in online}}
