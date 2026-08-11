# 04 — Game player profile

**Complexity:** Intermediate  
**Focus:** typed DDM subclasses, nested DDM composition, ListDDM, DDMSearchEngine

## Scenario

Model a game player with nested combat statistics, calculate power, and efficiently find high-level or high-win players.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
04_game_player_profile/
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

- Store inventory as nested `Item(DDM)` objects.
- Use `ListDDM.top("stats.wins")` for leaderboards.
- Use `BatchPlan` for season-wide stat transformations.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
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
```

### `repository.py`

```python
from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import Player


class PlayerRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(Player(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'level', 'team', 'stats.wins')

    def by_id(self, value: int) -> Player | None:
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
from repository import PlayerRepository


class PlayerService:
    def __init__(self, repository: PlayerRepository):
        self.repository = repository

    def demo(self):
        lions = self.repository.where(team="lion", level__ge=20)
        for p in lions:
            p.grant_xp(250)
        return [(p.name, round(p.win_rate, 3), p.xp) for p in lions]
```

### `main.py`

```python
from __future__ import annotations
import json
from pathlib import Path
from repository import PlayerRepository
from service import PlayerService

DATA = Path(__file__).with_name("data.json")
rows = json.loads(DATA.read_text(encoding="utf-8"))
repo = PlayerRepository(rows)
service = PlayerService(repo)

print("records:", len(repo.items))
print("first:", repo.items[0].to_dict())
print("result:", service.demo())
print("index stats:", repo.search.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

