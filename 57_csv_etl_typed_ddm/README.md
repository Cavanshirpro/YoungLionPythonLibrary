# 57 — CSV ETL into typed DDM records

**Complexity:** Intermediate  
**Focus:** File CSV, typed DDM, DDMTable, ETL

## Scenario

Read tabular customer data, normalize it into typed DDM models, perform collection analytics, and write a clean CSV export.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
57_csv_etl_typed_ddm/
├── models.py
├── main.py
```

## What to pay attention to

- **File CSV** — used as part of the actual workflow, not only imported for demonstration.
- **typed DDM** — used as part of the actual workflow, not only imported for demonstration.
- **DDMTable** — used as part of the actual workflow, not only imported for demonstration.
- **ETL** — used as part of the actual workflow, not only imported for demonstration.

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

- Add validation/error rows instead of failing the entire import.
- Chunk huge inputs.
- Index the resulting customer collection.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from YoungLion import DDM
class Customer(DDM):
    def __init__(self,d): super().__init__(d); self.id=int(d.get("id",0)); self.name=str(d.get("name","" )).strip(); self.country=str(d.get("country","Unknown")).upper(); self.spend=float(d.get("spend",0))
```

### `main.py`

```python
from tempfile import TemporaryDirectory
from YoungLion import File, DDMTable
from models import Customer
with TemporaryDirectory() as tmp:
    f=File(tmp)
    f.csv_write("input.csv",[{"id":"1","name":" Alice ","country":"us","spend":"120.5"},{"id":"2","name":"Cavan","country":"az","spend":"410"},{"id":"3","name":"Bob","country":"de","spend":"75"}])
    customers=DDMTable(Customer(row) for row in f.csv_read("input.csv"))
    print("mean spend",customers.mean("spend"),"countries",customers.distinct("country"))
    f.csv_write("clean.csv",[{k:str(v) for k,v in row.items()} for row in customers.select("id","name","country","spend")])
    print(f.txt_read_str("clean.csv"))
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

