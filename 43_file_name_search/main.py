from pathlib import Path
from YoungLion import FileSearchEngine

root = Path(__file__).parent / "workspace"
root.mkdir(exist_ok=True)
(root / "user_settings.json").write_text("{}", encoding="utf-8")
(root / "database_backup.txt").write_text("backup", encoding="utf-8")
engine = FileSearchEngine(root)
print(engine.search("settings"))
