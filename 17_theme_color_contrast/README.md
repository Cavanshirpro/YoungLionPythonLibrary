# 17. Theme color contrast

## Scenario

Evaluate UI color contrast and blending.

## Project structure

```text
17_theme_color_contrast/
├── README.md
└── main.py
```

## YoungLion concepts

- `Color`
- `hex`
- `contrast`
- `blend`

## Run

```bash
cd 17_theme_color_contrast
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Evaluate UI color contrast and blending. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
from YoungLion import Color

background = Color.from_hex("#202124")
foreground = Color.from_hex("#FFFFFF")
print("Contrast:", background.contrast_ratio(foreground))
print("Blend:", background.blend(foreground, 0.2).to_hex())
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
Contrast: 16.098951261824404
Blend: #4D4D50
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
