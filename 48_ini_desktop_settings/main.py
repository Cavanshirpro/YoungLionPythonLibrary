from pathlib import Path
from YoungLion import File

f = File(str(Path(__file__).parent / "workspace"))
f.ini_write("app.ini", {"ui": {"theme": "dark", "scale": "1.25"}, "network": {"timeout": "20"}})
print(f.ini_read("app.ini"))
