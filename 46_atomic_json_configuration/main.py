from pathlib import Path
from YoungLion import File

root = Path(__file__).parent / "workspace"
f = File(str(root))
f.atomic_write_json("config.json", {"theme": "dark", "workers": 4})
print(f.json_read("config.json"))
print("SHA256:", f.checksum("config.json"))
