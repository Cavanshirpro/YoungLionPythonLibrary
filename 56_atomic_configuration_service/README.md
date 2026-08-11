# 56 — Atomic typed configuration service

**Complexity:** Intermediate  
**Focus:** File, atomic JSON, typed DDM configuration, checksum/backup

## Scenario

Persist a typed settings DDM safely using atomic JSON replacement, checksums and backup files. This resembles a desktop app configuration manager.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
56_atomic_configuration_service/
├── models.py
├── service.py
├── main.py
```

## What to pay attention to

- **File** — used as part of the actual workflow, not only imported for demonstration.
- **atomic JSON** — used as part of the actual workflow, not only imported for demonstration.
- **typed DDM configuration** — used as part of the actual workflow, not only imported for demonstration.
- **checksum/backup** — used as part of the actual workflow, not only imported for demonstration.

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

This project combines several YoungLion components behind a small service boundary. The emphasis is operational: safe file replacement, structured process results, caching/rate limiting, event delivery, search ownership or logging. Application code should consume the service rather than coordinate every utility directly.

The example stays network-free and credential-free. In a real application, external I/O belongs behind adapters where retry, circuit breaking, validation and logging policies can be tested independently.

## Ways to extend this project

- Add versioned migrations before constructing Settings.
- Validate checksum in a recovery routine.
- Use ViewDDM for an editor bound to the same mapping.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from YoungLion import DDM
class Ui(DDM):
    def __init__(self,d): super().__init__(d); self.theme=str(d.get("theme","dark")); self.scale=float(d.get("scale",1.0))
class Settings(DDM):
    def __init__(self,d): super().__init__(d); self.version=int(d.get("version",1)); self.autosave=bool(d.get("autosave",True)); self.ui=Ui(d.get("ui",{}))
```

### `service.py`

```python
from YoungLion import File
from models import Settings
class ConfigService:
    def __init__(self,root): self.files=File(root)
    def load(self): return Settings(self.files.json_read("settings.json",default={"version":1,"ui":{}}))
    def save(self,s): self.files.atomic_write_json("settings.json",s.to_dict()); return self.files.checksum("settings.json")
    def backup(self): return self.files.backup("settings.json")
```

### `main.py`

```python
from tempfile import TemporaryDirectory
from service import ConfigService
with TemporaryDirectory() as tmp:
    c=ConfigService(tmp); s=c.load(); s.ui.theme="light"; s.ui.scale=1.25; digest=c.save(s); backup=c.backup(); print(s.to_dict()); print("sha256",digest); print("backup",backup)
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

