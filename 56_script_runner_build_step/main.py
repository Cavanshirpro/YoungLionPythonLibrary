from pathlib import Path
import sys
from YoungLion import ScriptRunner

root = Path(__file__).parent / "workspace"
root.mkdir(exist_ok=True)
script = root / "child.py"
script.write_text("print('build step complete')\n", encoding="utf-8")
result = ScriptRunner(sys.executable).run([sys.executable, str(script)], check=True)
print(result.ok, result.stdout.strip(), round(result.duration, 4))
