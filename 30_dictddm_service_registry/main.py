from YoungLion import DictDDM
from models import Service

services = DictDDM({
    "auth": Service({"name":"Auth","status":"healthy","latency_ms":18}),
    "search": Service({"name":"Search","status":"healthy","latency_ms":42}),
    "media": Service({"name":"Media","status":"degraded","latency_ms":180}),
})
print("degraded keys:", services.keys_for("status","degraded"))
services.multiply("latency_ms", 1.05)
engine = services.indexed("status","latency_ms")
print("slow:", [s.name for s in engine.find("latency_ms",100,op="gt")])
