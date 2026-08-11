from YoungLion import ListDDM, DDM

rows = ListDDM(DDM({"id":i,"score":(i//3)*10}) for i in range(1000))
rows.sort_by("score", inplace=True)
start,end = rows.equal_range("score", 500)
print("score=500 slice:", [(r.id,r.score) for r in rows._items_snapshot()[start:end]])
print("lower bound 777:", rows.lower_bound("score",777))
print("binary 500:", rows.binary_search("score",500))
