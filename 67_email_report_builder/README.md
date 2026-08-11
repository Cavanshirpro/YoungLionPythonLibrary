# 67. E-mail report builder

## Scenario

Build a multipart e-mail locally without sending network traffic.

## Project structure

```text
67_email_report_builder/
├── README.md
└── main.py
```

## YoungLion concepts

- `EmailManager`
- `EmailMessage`
- `HTML`
- `attachments-ready API`

## Run

```bash
cd 67_email_report_builder
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Build a multipart e-mail locally without sending network traffic. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
from YoungLion import EmailManager

mail = EmailManager("smtp.example.invalid", 587, "bot@example.invalid", "not-a-real-password")
message = mail.build_email(
    "owner@example.invalid",
    "Daily report",
    "All services are healthy.",
    html="<b>All services are healthy.</b>",
)
print(message["Subject"])
print(message.get_content_type())
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
Daily report
multipart/alternative
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
