from pathlib import Path
from YoungLion import FileSearchEngine, ApplicationSearch, TTLCache, TextProcessor

root = Path(__file__).parent / "workspace" / "notes"
root.mkdir(parents=True, exist_ok=True)
(root / "native.md").write_text("YoungLion uses a C++ native extension for hot paths.", encoding="utf-8")
(root / "search.md").write_text("DDMSearchEngine indexes nested paths such as profile.name.", encoding="utf-8")

file_index = FileSearchEngine(root, content=True)
paths = file_index.search("nested path")
print("Matching files:", paths)

app = ApplicationSearch()
for i, path in enumerate(root.glob("*.md"), 1):
    text = path.read_text(encoding="utf-8")
    app.add(i, path.stem, text, payload=str(path))
print("Ranked:", app.search("native hot path"))

cache = TTLCache(default_ttl=60)
summary = TextProcessor((root / "native.md").read_text()).summarize(1)
cache.set("native-summary", summary)
print("Cached summary:", cache.get("native-summary"))
