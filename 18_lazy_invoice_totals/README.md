# 18 — LazyDDM invoice calculations

**Complexity:** Intermediate  
**Focus:** LazyDDM, derived fields, deferred computation

## Scenario

Keep expensive/derived invoice fields lazy until actually requested. The example separates source values from derived totals and shows cache-like access behavior.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
18_lazy_invoice_totals/
├── main.py
```

## What to pay attention to

- **LazyDDM** — used as part of the actual workflow, not only imported for demonstration.
- **derived fields** — used as part of the actual workflow, not only imported for demonstration.
- **deferred computation** — used as part of the actual workflow, not only imported for demonstration.

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

- Make line-item aggregation lazy for large invoices.
- Invalidate/rebuild derived values when source fields change.
- Compare with precomputed values in a benchmark.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import LazyDDM

invoice = LazyDDM(
    {"subtotal": 199.0, "tax_rate": 0.18, "shipping": 12.0},
    lazy={
        "tax": lambda d: round(d.subtotal * d.tax_rate, 2),
        "total": lambda d: round(d.subtotal + d.tax + d.shipping, 2),
    },
)
print("raw keys before access:", list(invoice.keys()))
print("total:", invoice.total)
print("serialized:", invoice.to_dict())
invoice.invalidate("tax", "total")
print("recomputed:", invoice.total)
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

