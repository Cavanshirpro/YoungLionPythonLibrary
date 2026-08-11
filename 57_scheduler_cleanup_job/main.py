from YoungLion import TaskScheduler

scheduler = TaskScheduler()
seen = []
task_id = scheduler.schedule_task(lambda: seen.append("cleanup"), delay=0.02, repeat=None)
info = scheduler.wait(task_id, timeout=1.0)
print(info.state if info else "timeout", seen)
scheduler.shutdown()
