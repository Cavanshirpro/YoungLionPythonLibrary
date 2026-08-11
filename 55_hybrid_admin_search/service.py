from YoungLion import ListDDM, DDMSearchEngine, ApplicationSearch
from models import User
class AdminSearch:
    def __init__(self,rows):
        self.users=ListDDM(User(r) for r in rows); self.paths=DDMSearchEngine(self.users).create_indexes("id","active","role","profile.country"); self.text=ApplicationSearch()
        for u in self.users: self.text.add(u.id,title=f"{u.profile.name} @{u.username}",body=f"{u.role} {u.profile.country}",fields={"role":u.role,"country":u.profile.country},payload=u)
    def query(self,text,country=None,active=None):
        candidates=self.text.search(text,limit=50); allowed={id(x) for x in candidates}
        if country is not None: allowed &= {id(x) for x in self.paths.find("profile.country",country)}
        if active is not None: allowed &= {id(x) for x in self.paths.find("active",active)}
        return [u for u in candidates if id(u) in allowed]
