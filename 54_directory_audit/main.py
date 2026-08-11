from pathlib import Path
from YoungLion import File

root = Path(__file__).parent / "workspace"
f = File(str(root))
f.txt_write_str("logs/a.log", "hello")
f.txt_write_str("logs/b.log", "world")
for path in f.find_files("*.log", recursive=True):
    print(path, f.get_info(path).get("size"), f.checksum(path)[:12])
print("Directory bytes:", f.directory_size())
