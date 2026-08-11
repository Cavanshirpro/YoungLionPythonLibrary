from YoungLion import DDM
class Event(DDM):
    def __init__(self,data):
        super().__init__(data); self.id=int(data.get("id",0)); self.event_id=str(data.get("event_id","")); self.type=str(data.get("type",""))
