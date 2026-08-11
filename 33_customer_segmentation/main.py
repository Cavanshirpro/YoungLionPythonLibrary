from YoungLion import ListDDM
from models import Customer

customers = ListDDM(Customer({"id":i,"country":["AZ","US","DE"][i%3],"tier":["free","pro","team"][i%3],"spend":(i*17)%5000}) for i in range(5000))
print("countries:", customers.distinct("country"))
print("tier counts:", customers.count_by("tier"))
for country, rows in customers.group_by("country").items():
    group = ListDDM(rows)
    print(country, "users", len(group), "mean spend", round(group.mean("spend") or 0,2))
