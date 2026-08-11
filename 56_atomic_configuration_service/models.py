from YoungLion import DDM
class Ui(DDM):
    def __init__(self,d): super().__init__(d); self.theme=str(d.get("theme","dark")); self.scale=float(d.get("scale",1.0))
class Settings(DDM):
    def __init__(self,d): super().__init__(d); self.version=int(d.get("version",1)); self.autosave=bool(d.get("autosave",True)); self.ui=Ui(d.get("ui",{}))
