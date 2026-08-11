from YoungLion import ListDDM, DDMSearchEngine
from models import User
users=ListDDM(User({"id":i,"username":f"u{i}","profile":{"name":f"N{i}","age":10+i%70,"country":"AZ","city":"Baku"}}) for i in range(20000))
engine=DDMSearchEngine(users).create_indexes("profile.age")
for low,high in [(18,25),(26,40),(41,65)]:
    rows=engine.between("profile.age",low,high)
    print((low,high),len(rows),rows[0].profile.age if rows else None)
