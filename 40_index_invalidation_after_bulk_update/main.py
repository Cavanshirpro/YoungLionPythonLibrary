from YoungLion import ListDDM, DDM, DDMSearchEngine

users = ListDDM(DDM({"id":i,"profile":{"country":"AZ" if i%2 else "US"}}) for i in range(1000))
engine = DDMSearchEngine(users).create_indexes("profile.country")
users._search_engine = engine
print("AZ before:", engine.count("profile.country","AZ"))
users.set_all("profile.country","AZ")
print("AZ after:", engine.count("profile.country","AZ"))
print("stats:", engine.stats())
