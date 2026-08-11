# 17 — DefaultDDM feature flag configuration

**Complexity:** Intermediate  
**Focus:** DefaultDDM, configuration defaults, nested paths

## Scenario

Build environment-specific feature configuration where absent values fall back predictably, while explicit overrides remain serializable.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
17_default_feature_flags/
├── main.py
├── config_notes.md
```

## What to pay attention to

- **DefaultDDM** — used as part of the actual workflow, not only imported for demonstration.
- **configuration defaults** — used as part of the actual workflow, not only imported for demonstration.
- **nested paths** — used as part of the actual workflow, not only imported for demonstration.

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

This project isolates one specialized DDM/model capability and demonstrates the tradeoff that justifies it. Variants are not intended to replace normal `DDM` everywhere: choose them when immutability, identity hashing, lazy computation, defaults, validation, zero-copy views or memory density materially change the problem.

Keep the specialized boundary explicit. Convert to a richer typed domain subclass when domain behavior becomes more important than the storage/semantic specialization.

## Ways to extend this project

- Load overrides from JSON with File.
- Create typed wrapper methods such as `is_enabled(name)`.
- Add environment-specific merge layers with DDM.merge.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import DefaultDDM

flags = DefaultDDM(
    {"search_v2": {"enabled": True, "rollout": 25}},
    default_factory=lambda: {"enabled": False, "rollout": 0},
)
print("existing:", flags.search_v2)
print("missing payments_v2:", flags.payments_v2)
flags.set_path("payments_v2.enabled", True)
print(flags.to_dict())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

