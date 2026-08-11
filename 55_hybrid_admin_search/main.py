from service import AdminSearch
rows=[{"id":i,"username":f"user{i}","role":"admin" if i%100==0 else "member","active":i%7!=0,"profile":{"name":f"Cavan {i}" if i%50==0 else f"Person {i}","age":18+i%40,"country":"AZ" if i%3==0 else "US","city":""}} for i in range(5000)]
s=AdminSearch(rows)
print([(u.id,u.username,u.profile.country) for u in s.query("cavn",country="AZ",active=True)[:10]])
