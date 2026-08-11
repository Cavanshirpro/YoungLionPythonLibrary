from YoungLion import DDM
class Player(DDM):
    def __init__(self,data):
        super().__init__(data); self.id=int(data.get("id",0)); self.name=str(data.get("name","")); self.score=float(data.get("score",0)); self.team=str(data.get("team","solo"))
