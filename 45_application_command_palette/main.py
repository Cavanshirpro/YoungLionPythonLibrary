from YoungLion import ApplicationSearch
from commands import COMMANDS
engine=ApplicationSearch()
for c in COMMANDS:
    engine.add(c["id"],title=c["title"],body=c["body"],fields={"category":c["category"]},payload=c)
for q in ["setings","profil","find file"]:
    print(q,[r["title"] for r in engine.search(q,limit=3)])
print("suggest:",[x.term for x in engine.suggest("gen")])
print("facets:",engine.facet("category"))
