from YoungLion import ListDDM, DDMSearchEngine
from models import User
names=["Cavanshir Qurbanzade","Alice Johnson","Robert Stone","Alicia Keys","Catherine Green"]
users=ListDDM(User({"id":i,"username":n.split()[0].lower(),"profile":{"name":n,"age":20+i,"country":"AZ" if i==0 else "US","city":""}}) for i,n in enumerate(names))
engine=DDMSearchEngine(users).create_indexes("profile.name")
for q in ["Cavansir","Alcie","Robrt"]:
    hits=engine.text("profile.name",q,hits=True,limit=3)
    print(q,[(h.item.profile.name,round(h.score,3),h.algorithm) for h in hits])
