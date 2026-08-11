from pathlib import Path
from YoungLion import ScriptRunner, RetryPolicy, Stopwatch
runner=ScriptRunner()
worker=str(Path(__file__).with_name("worker.py"))
with Stopwatch() as sw:
    result=RetryPolicy(attempts=3,delay=0.01).call(lambda: runner.run(["python",worker,"build","--strict"],check=True))
print("ok",result.ok,"stdout",result.stdout.strip(),"elapsed",round(sw.elapsed,4))
