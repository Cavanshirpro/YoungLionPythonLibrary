from directory import UserDirectory
rows=[{"id":i,"username":f"user{i}","role":"admin" if i%50==0 else "member","active":True,"profile":{"name":f"User {i}","age":15+i%50,"country":["AZ","US","DE"][i%3],"city":"Baku" if i%3==0 else ""}} for i in range(10000)]
d=UserDirectory(rows)
print("lookup:",d.username("user7345").profile.to_dict())
print("AZ:",len(d.country("AZ")),"adults:",len(d.adults()))
print(d.engine.stats())
