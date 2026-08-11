# 07 — Application settings model tree

**Complexity:** Intermediate  
**Focus:** typed DDM subclasses, nested DDM composition, ListDDM, DDMSearchEngine

## Scenario

Represent desktop application settings using typed nested models, controlled update methods and indexed profile selection.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
07_application_settings_models/
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

- Save the selected profile with `File.atomic_write_json`.
- Add audio/network nested DDMs.
- Use `ViewDDM` for an editable view over a shared settings mapping.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class UiSettings(DDM):
    theme: str
    scale: float
    language: str

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.theme = str(data.get('theme', "dark"))
        self.scale = float(data.get('scale', 1.0))
        self.language = str(data.get('language', "en"))


class SettingsProfile(DDM):
    id: int
    name: str
    active: bool
    autosave_seconds: int
    ui: UiSettings

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.name = str(data.get('name', "Default"))
        self.active = bool(data.get('active', False))
        self.autosave_seconds = int(data.get('autosave_seconds', 30))
        self.ui = UiSettings(data.get('ui', {}))

    def activate(self) -> None:
        self.active = True

    def set_scale(self, scale: float) -> None:
        if not 0.5 <= scale <= 3.0: raise ValueError("unsupported scale")
        self.ui.scale = scale
```

### `repository.py`

```python
from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import SettingsProfile


class SettingsProfileRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(SettingsProfile(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'active', 'ui.theme', 'ui.language')

    def by_id(self, value: int) -> SettingsProfile | None:
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
from repository import SettingsProfileRepository


class SettingsProfileService:
    def __init__(self, repository: SettingsProfileRepository):
        self.repository = repository

    def demo(self):
        current = self.repository.search.find_one("active", True)
        assert current is not None
        current.set_scale(1.15)
        return current.to_dict()
```

### `main.py`

```python
from __future__ import annotations
import json
from pathlib import Path
from repository import SettingsProfileRepository
from service import SettingsProfileService

DATA = Path(__file__).with_name("data.json")
rows = json.loads(DATA.read_text(encoding="utf-8"))
repo = SettingsProfileRepository(rows)
service = SettingsProfileService(repo)

print("records:", len(repo.items))
print("first:", repo.items[0].to_dict())
print("result:", service.demo())
print("index stats:", repo.search.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

