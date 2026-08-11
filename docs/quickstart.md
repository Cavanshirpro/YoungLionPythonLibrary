# Quick start

## DDM
```python
from YoungLion import DDM
record = DDM({"profile": {"name": "Nora"}, "score": 10})
record.set_path("profile.level", 4)
record.score += 5
```

## Collection
```python
from YoungLion import ListDDM
rows = ListDDM({"id": i, "score": i * 10} for i in range(5))
rows.increment("score", 2)
print(rows.top("score", 2))
```

## Search
```python
from YoungLion import DDMSearchEngine
engine = DDMSearchEngine(rows)
engine.create_index("id")
print(engine.find("id", 3))
```

## File
```python
from YoungLion import File
f = File("./state")
f.atomic_write_json("settings.json", {"theme": "dark"})
```
