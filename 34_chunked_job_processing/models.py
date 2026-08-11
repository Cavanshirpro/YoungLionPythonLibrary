from YoungLion import DDM
class Job(DDM):
    def __init__(self,data):
        super().__init__(data); self.id=int(data.get("id",0)); self.state=str(data.get("state","queued")); self.attempts=int(data.get("attempts",0))
