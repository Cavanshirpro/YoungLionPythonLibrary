# 02 — Discord-style guild member model

**Complexity:** Intermediate  
**Focus:** typed DDM subclasses, nested DDM composition, ListDDM, DDMSearchEngine

## Scenario

Represent guild members with nested moderation state and perform indexed moderation queries without coupling the model to a Discord SDK.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
02_discord_guild_member/
├── models.py
├── repository.py
├── service.py
├── main.py
├── data.json
```

## What to pay attention to

- **typed DDM subclasses** — used as part of the actual workflow, not only imported for demonstration.
- **nested DDM composition** — used as part of the actual workflow, not only imported for demonstration.
- **ListDDM** — used as part of the actual workflow, not only imported for demonstration.
- **DDMSearchEngine** — used as part of the actual workflow, not only imported for demonstration.

## Run

From this directory:

```bash
python main.py
```

Install YoungLion first. After v0.1 is published:

```bash
python -m pip install YoungLion==0.1.0
```

During local pre-release development you can instead install the main branch checkout with `python -m pip install -e <path-to-main-checkout>`.

## Design notes

### Architecture walkthrough

This project uses a **domain-model → repository/index → service → entry-point** split. DDM subclasses own normalization and local invariants; the repository owns `ListDDM` and `DDMSearchEngine`; the service coordinates the use case. This is a practical shape when `class User(DDM)` grows beyond a small script.

Nested mappings are deliberately replaced by typed DDM objects during construction. That gives the IDE real attributes such as `user.profile.country`, while `to_dict()`, `get_path("profile.country")`, collection batch operations and nested indexes continue to work. Unknown input keys can remain available for forward compatibility.

## Ways to extend this project

- Connect the model to your Discord bot adapter without importing discord.py in the model layer.
- Use `BatchPlan` to apply periodic rewards to thousands of members.
- Index `moderation.reason` with text search.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
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
```

### `repository.py`

```python
from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import GuildMember


class GuildMemberRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(GuildMember(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'level', 'moderation.warnings', 'moderation.muted')

    def by_id(self, value: int) -> GuildMember | None:
        return self.search.find_one("id", value)

    def where(self, **lookups):
        return self.search.where(**lookups)

    def refresh(self) -> None:
        self.search.refresh()

    def snapshot(self) -> list[dict]:
        return [item.to_dict() for item in self.items]
```

### `service.py`

```python
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
```

### `main.py`

```python
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
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

