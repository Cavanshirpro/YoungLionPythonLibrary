from YoungLion import ListDDM, DDMSearchEngine
from models import User
class Repository:
    def __init__(self,rows):
        self.rows=ListDDM(User(r) for r in rows); self.engine=DDMSearchEngine(self.rows); self.engine.create_indexes("id","role","active","profile.name","profile.age","profile.country")
    def find_user(self,id): return self.engine.find_one("id",id)
    def admin_candidates(self,country): return self.engine.where(role="member",active=True,profile__country=country,profile__age__ge=18)
    def name_search(self,q): return self.engine.text("profile.name",q,limit=10)
