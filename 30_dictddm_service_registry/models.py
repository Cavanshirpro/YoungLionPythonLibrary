from YoungLion import DDM
class Service(DDM):
    def __init__(self,data):
        super().__init__(data); self.name=str(data.get("name","")); self.status=str(data.get("status","unknown")); self.latency_ms=float(data.get("latency_ms",0))
