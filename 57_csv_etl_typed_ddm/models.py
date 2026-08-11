from YoungLion import DDM
class Customer(DDM):
    def __init__(self,d): super().__init__(d); self.id=int(d.get("id",0)); self.name=str(d.get("name","" )).strip(); self.country=str(d.get("country","Unknown")).upper(); self.spend=float(d.get("spend",0))
