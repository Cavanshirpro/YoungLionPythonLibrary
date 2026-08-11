from YoungLion import DDM
class Account(DDM):
    def __init__(self,data):
        super().__init__(data); self.id=int(data.get("id",0)); self.email=str(data.get("email","")); self.score=float(data.get("score",0))
