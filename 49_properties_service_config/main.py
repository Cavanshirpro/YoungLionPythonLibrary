from pathlib import Path
from YoungLion import File

f = File(str(Path(__file__).parent / "workspace"))
f.properties_write("service.properties", {"service.name": "younglion", "workers": "4"})
print(f.properties_read("service.properties"))
