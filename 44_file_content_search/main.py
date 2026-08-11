from pathlib import Path
from YoungLion import FileSearchEngine

root = Path(__file__).parent / "workspace"
root.mkdir(exist_ok=True)
(root / "network.md").write_text("Reverse proxy and TLS configuration guide", encoding="utf-8")
(root / "python.md").write_text("Python native extension build notes", encoding="utf-8")
engine = FileSearchEngine(root, content=True, extensions=[".md"])
print(engine.search("native extension"))
