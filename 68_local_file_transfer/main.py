from pathlib import Path
from YoungLion import FileTransferManager

root = Path(__file__).parent / "workspace"
root.mkdir(exist_ok=True)
source = root / "source.txt"
dest = root / "copy.txt"
source.write_text("transfer me", encoding="utf-8")
manager = FileTransferManager()
tid = manager.upload(str(source), str(dest), protocol="local")
print(manager.get_status(tid), manager.get_progress(tid), dest.read_text())
