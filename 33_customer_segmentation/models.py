from YoungLion import DDM
class Customer(DDM):
    def __init__(self,data):
        super().__init__(data); self.id=int(data.get("id",0)); self.country=str(data.get("country","")); self.tier=str(data.get("tier","free")); self.spend=float(data.get("spend",0))
