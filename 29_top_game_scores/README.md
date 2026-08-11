# 29. Leaderboard selection

## Scenario

Use top/nth operations for a game leaderboard.

## Project structure

```text
29_top_game_scores/
├── README.md
└── main.py
```

## YoungLion concepts

- `top`
- `nth`
- `numeric reduction`

## Run

```bash
cd 29_top_game_scores
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Use top/nth operations for a game leaderboard. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
from YoungLion import ListDDM

players = ListDDM({"name": f"P{i}", "score": (i * 17) % 101} for i in range(12))
print("Top 3:", [(p.name, p.score) for p in players.top("score", 3)])
print("Average:", players.mean("score"))
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
Top 3: [('P11', 86), ('P5', 85), ('P10', 69)]
Average: 43.0
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
