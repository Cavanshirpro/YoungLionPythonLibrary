# 66. CLI color theme

## Scenario

Use true color and ANSI-safe wrapping for a CLI.

## Project structure

```text
66_cli_color_theme/
├── README.md
└── main.py
```

## YoungLion concepts

- `Colors`
- `RGB`
- `wrap`
- `strip`

## Run

```bash
cd 66_cli_color_theme
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Use true color and ANSI-safe wrapping for a CLI. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
from YoungLion import Colors

styled = Colors.wrap("YoungLion", Colors.BOLD if hasattr(Colors, "BOLD") else Colors.BRIGHT, Colors.rgb(255, 180, 0))
print(styled)
print("Plain:", Colors.strip(styled))
print("Gradient:", Colors.gradient("native", (255, 80, 30), (80, 160, 255)))
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
[1m[38;2;255;180;0mYoungLion[0m
Plain: YoungLion
Gradient: [38;2;255;80;30mn[38;2;220;96;75ma[38;2;185;112;120mt[38;2;150;128;165mi[38;2;115;144;210mv[38;2;80;160;255me[0m
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
