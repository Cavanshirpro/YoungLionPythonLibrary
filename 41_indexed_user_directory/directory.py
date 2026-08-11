from YoungLion import ListDDM, DDMSearchEngine
from models import User
class UserDirectory:
    def __init__(self,rows):
        self.users=ListDDM(User(x) for x in rows)
        self.engine=self.users.indexed("id","username","role","profile.country","profile.age")
    def username(self,value): return self.engine.find_one("username",value)
    def country(self,value): return self.engine.find("profile.country",value)
    def adults(self): return self.engine.find("profile.age",18,op="ge")
