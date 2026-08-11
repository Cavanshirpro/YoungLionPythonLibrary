# 64. Article text analysis

## Scenario

Compute common content metrics and extract entities.

## Project structure

```text
64_text_article_analysis/
├── README.md
└── main.py
```

## YoungLion concepts

- `TextProcessor`
- `ngrams`
- `URLs/e-mails`
- `readability`

## Run

```bash
cd 64_text_article_analysis
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Compute common content metrics and extract entities. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
from YoungLion import TextProcessor

text = "Contact team@example.com. Read https://example.com/docs for YoungLion documentation. YoungLion is fast."
tp = TextProcessor(text)
print(tp.stats())
print("Emails:", tp.extract_emails())
print("URLs:", tp.extract_urls())
print("Top words:", tp.most_frequent_words(5))
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
{'characters': 103, 'characters_no_spaces': 94, 'words': 15, 'unique_words': 12, 'sentences': 3, 'lines': 1, 'readability': 55.12000000000003}
Emails: ['team@example.com']
URLs: ['https://example.com/docs']
Top words: [('example', 2), ('com', 2), ('younglion', 2), ('contact', 1), ('team', 1)]
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
