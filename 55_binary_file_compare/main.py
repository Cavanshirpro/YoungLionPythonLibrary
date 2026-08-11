from pathlib import Path
from YoungLion import File

f = File(str(Path(__file__).parent / "workspace"))
payload = bytes([0, 1]) + b"YoungLion" + bytes([255])
f.write_bytes("a.bin", payload)
f.write_bytes("b.bin", payload)
print("Equal:", f.compare_files("a.bin", "b.bin"))
print("SHA256:", f.checksum("a.bin"))
