from YoungLion import ListDDM
from models import Job

jobs = ListDDM(Job({"id":i,"state":"queued","attempts":0}) for i in range(10000))
processed=0
for chunk in jobs.chunks(750):
    batch = ListDDM(chunk)
    batch.set_all("state","processed")
    batch.increment("attempts",1)
    processed += len(batch)
print("processed:", processed, "states:", jobs.count_by("state"), "attempts:", jobs.sum("attempts"))
