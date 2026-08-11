from pathlib import Path
from YoungLion import Logger

path = Path(__file__).parent / "workspace" / "app.log"
path.parent.mkdir(exist_ok=True)
log = Logger(str(path), "INFO", console=False, max_bytes=2048, backup_count=2)
log.bind(component="payments", request_id="r-17").info("payment validated", amount=42.5)
print(path.read_text(encoding="utf-8").strip())
