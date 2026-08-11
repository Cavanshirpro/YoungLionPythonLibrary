from pathlib import Path
from YoungLion import File

root = Path(__file__).parent / "workspace"
f = File(str(root))
f.txt_write_str("important.txt", "critical local state\n")
backup = f.backup("important.txt")
print("Backup:", backup)
print("Original SHA:", f.checksum("important.txt"))
print("Same bytes:", f.compare_files("important.txt", backup))
