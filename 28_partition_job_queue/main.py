from YoungLion import ListDDM

jobs = ListDDM({"id": i, "state": "ready" if i % 2 == 0 else "waiting"} for i in range(8))
ready, waiting = jobs.partition_path("state", "ready")
print("ready:", len(ready), "waiting:", len(waiting))
