from pathlib import Path
from YoungLion import File

f = File(str(Path(__file__).parent / "workspace"))
f.yaml_write("app.yaml", {"app": {"name": "YoungLion", "debug": True}, "workers": 4})
print(f.yaml_read("app.yaml"))
