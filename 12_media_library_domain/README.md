# 12 — Media library domain

**Complexity:** Intermediate  
**Focus:** typed DDM subclasses, nested DDM composition, ListDDM, DDMSearchEngine

## Scenario

Keep media metadata and nested technical properties typed while supporting indexed filtering by codec, resolution and favorite state.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
12_media_library_domain/
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

- Use FileSearchEngine to discover media metadata files.
- Add a SearchIndex for titles/descriptions.
- Store per-item generated checksums with `File.checksum`.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class MediaInfo(DDM):
    codec: str
    width: int
    height: int
    duration: float

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.codec = str(data.get('codec', ""))
        self.width = int(data.get('width', 0))
        self.height = int(data.get('height', 0))
        self.duration = float(data.get('duration', 0.0))


class MediaItem(DDM):
    id: int
    title: str
    kind: str
    favorite: bool
    rating: int
    media: MediaInfo

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.title = str(data.get('title', ""))
        self.kind = str(data.get('kind', "video"))
        self.favorite = bool(data.get('favorite', False))
        self.rating = int(data.get('rating', 0))
        self.media = MediaInfo(data.get('media', {}))

    def is_4k(self) -> bool:
        return self.media.width >= 3840 and self.media.height >= 2160

    def favorite_it(self) -> None:
        self.favorite = True
```

### `repository.py`

```python
from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import MediaItem


class MediaItemRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(MediaItem(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'kind', 'favorite', 'rating', 'media.codec', 'media.width')

    def by_id(self, value: int) -> MediaItem | None:
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
from repository import MediaItemRepository


class MediaItemService:
    def __init__(self, repository: MediaItemRepository):
        self.repository = repository

    def demo(self):
        videos = self.repository.where(kind="video", rating__ge=4)
        return [(m.title, m.media.codec, m.is_4k()) for m in videos]
```

### `main.py`

```python
from __future__ import annotations
import json
from pathlib import Path
from repository import MediaItemRepository
from service import MediaItemService

DATA = Path(__file__).with_name("data.json")
rows = json.loads(DATA.read_text(encoding="utf-8"))
repo = MediaItemRepository(rows)
service = MediaItemService(repo)

print("records:", len(repo.items))
print("first:", repo.items[0].to_dict())
print("result:", service.demo())
print("index stats:", repo.search.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

