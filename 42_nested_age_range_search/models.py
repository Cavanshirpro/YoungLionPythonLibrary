from YoungLion import DDM
class Profile(DDM):
    def __init__(self,data):
        super().__init__(data); self.name=str(data.get("name","Unknown")); self.age=int(data.get("age",0)); self.country=str(data.get("country","Unknown")); self.city=str(data.get("city",""))
class User(DDM):
    def __init__(self,data):
        super().__init__(data); self.id=int(data.get("id",0)); self.username=str(data.get("username","")); self.role=str(data.get("role","member")); self.active=bool(data.get("active",True)); self.profile=Profile(data.get("profile",{}))
