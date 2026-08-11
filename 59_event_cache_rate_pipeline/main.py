from service import ProfileService
s=ProfileService(); seen=[]; s.bus.subscribe("loaded",lambda row: seen.append(row["id"]))
for id in [1,1,2,2,1,3]: print(s.get(id))
print("backend calls",s.calls,"events",seen,"cache",s.cache.stats())
