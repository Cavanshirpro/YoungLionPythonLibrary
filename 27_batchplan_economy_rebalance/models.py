from YoungLion import DDM
class Player(DDM):
    def __init__(self,data):
        super().__init__(data); self.id=int(data.get("id",0)); self.wallet=float(data.get("wallet",0)); self.reputation=int(data.get("reputation",0)); self.active=bool(data.get("active",True))
