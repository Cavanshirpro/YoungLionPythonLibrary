from pathlib import Path
from YoungLion import File

root = Path(__file__).parent / "workspace"
f = File(str(root))
f.txt_write_str("large.txt", "YoungLion data line\n" * 1000)
bytes_seen = sum(len(chunk) for chunk in f.read_chunks("large.txt", chunk_size=4096))
print("Bytes processed:", bytes_seen)
