from repository import Repository
rows=[{"id":i,"username":f"u{i}","role":"member","active":i%9!=0,"profile":{"name":f"Person {i}","age":15+i%50,"country":["AZ","US","DE"][i%3],"city":""}} for i in range(30000)]
r=Repository(rows)
print(r.find_user(27654).username)
print("candidates:",len(r.admin_candidates("AZ")))
print("fuzzy:",[u.id for u in r.name_search("Persn 321")[:3]])
print(r.engine.stats())
