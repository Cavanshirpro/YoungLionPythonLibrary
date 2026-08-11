# 38. BM25 knowledge-base search

## Scenario

Rank longer support articles using an inverted index and BM25.

## Project structure

```text
38_bm25_knowledge_articles/
├── README.md
└── main.py
```

## YoungLion concepts

- `BM25Index`
- `SearchDocument`
- `full-text ranking`

## Run

```bash
cd 38_bm25_knowledge_articles
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Rank longer support articles using an inverted index and BM25. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

## Production extensions

- Replace the small in-memory sample with application data.
- Add tests around the public API used by this example.
- Add domain-specific validation/error handling before production use.

## Notes

- No real credentials are embedded.
- The example is designed for YoungLion 0.1.0 / CPython 3.10+.
- For performance-sensitive code, benchmark with data shaped like your actual workload.

## Full example code

```python
from YoungLion import BM25Index, SearchDocument

index = BM25Index([
    SearchDocument(1, "Reset your password from account security settings"),
    SearchDocument(2, "Change application appearance and dark mode"),
    SearchDocument(3, "Recover a locked account using backup codes"),
])
for result in index.search("account recovery backup"):
    print(result.document.id, round(result.score, 3), result.document.text)
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
3 1.419 Recover a locked account using backup codes
1 0.46 Reset your password from account security settings
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
