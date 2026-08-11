from YoungLion import DDM
class Customer(DDM):
    def __init__(self,d): super().__init__(d); self.country=str(d.get("country","")); self.tier=str(d.get("tier","free"))
class Order(DDM):
    def __init__(self,d): super().__init__(d); self.id=int(d.get("id",0)); self.tenant=str(d.get("tenant","default")); self.status=str(d.get("status","pending")); self.total=float(d.get("total",0)); self.customer=Customer(d.get("customer",{}))
