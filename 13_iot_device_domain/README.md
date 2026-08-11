# 13 — IoT device state domain

**Complexity:** Intermediate  
**Focus:** typed DDM subclasses, nested DDM composition, ListDDM, DDMSearchEngine

## Scenario

Normalize device state packets into nested typed models and query fleets by site, connectivity and temperature.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
13_iot_device_domain/
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

- Batch-update firmware version after a deployment.
- Use NumericSearch for nearest telemetry values.
- Use RateLimiter before talking to real devices.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class Telemetry(DDM):
    temperature: float
    voltage: float
    signal: int

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.temperature = float(data.get('temperature', 0.0))
        self.voltage = float(data.get('voltage', 0.0))
        self.signal = int(data.get('signal', 0))


class Device(DDM):
    id: int
    name: str
    site: str
    online: bool
    firmware: str
    telemetry: Telemetry

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.name = str(data.get('name', ""))
        self.site = str(data.get('site', ""))
        self.online = bool(data.get('online', False))
        self.firmware = str(data.get('firmware', ""))
        self.telemetry = Telemetry(data.get('telemetry', {}))

    def healthy(self) -> bool:
        return self.online and 2.8 <= self.telemetry.voltage <= 3.4 and self.telemetry.temperature < 60

    def update_firmware(self, version: str) -> None:
        self.firmware = version
```

### `repository.py`

```python
from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import Device


class DeviceRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(Device(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'site', 'online', 'firmware', 'telemetry.temperature')

    def by_id(self, value: int) -> Device | None:
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
from repository import DeviceRepository


class DeviceService:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository

    def demo(self):
        lab = self.repository.where(site="lab", online=True)
        return {d.name: d.healthy() for d in lab}
```

### `main.py`

```python
from __future__ import annotations
import json
from pathlib import Path
from repository import DeviceRepository
from service import DeviceService

DATA = Path(__file__).with_name("data.json")
rows = json.loads(DATA.read_text(encoding="utf-8"))
repo = DeviceRepository(rows)
service = DeviceService(repo)

print("records:", len(repo.items))
print("first:", repo.items[0].to_dict())
print("result:", service.demo())
print("index stats:", repo.search.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

