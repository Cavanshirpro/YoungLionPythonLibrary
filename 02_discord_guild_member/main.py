from __future__ import annotations
import json
from pathlib import Path
from repository import GuildMemberRepository
from service import GuildMemberService

DATA = Path(__file__).with_name("data.json")
rows = json.loads(DATA.read_text(encoding="utf-8"))
repo = GuildMemberRepository(rows)
service = GuildMemberService(repo)

print("records:", len(repo.items))
print("first:", repo.items[0].to_dict())
print("result:", service.demo())
print("index stats:", repo.search.stats())
