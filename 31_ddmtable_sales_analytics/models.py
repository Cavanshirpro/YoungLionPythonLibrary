from YoungLion import DDM
class Sale(DDM):
    def __init__(self,data):
        super().__init__(data); self.id=int(data.get("id",0)); self.region=str(data.get("region","")); self.amount=float(data.get("amount",0)); self.quantity=int(data.get("quantity",0))
