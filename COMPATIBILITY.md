# Compatibility Notes — pre-native to 0.1

The detailed compatibility policy is in [`docs/compatibility.md`](docs/compatibility.md), and migration guidance is in [`docs/migration-0.1.md`](docs/migration-0.1.md).

Primary preserved imports include:

```python
from YoungLion import DDM, File
from YoungLion.DataModel import DDM, Range, Vector, Timeline, Dataset, SmartCache, DDMBuilder
from YoungLion.function import File, Debugger, ScriptRunner, TaskScheduler, Logger
from YoungLion.search import Search, SearchData, SearchFile
```

The largest packaging change is intentional: 0.1 declares no third-party runtime Python dependencies. Advanced behavior that historically depended on large optional libraries is either implemented natively/with the standard library or documented as a compatibility boundary.
