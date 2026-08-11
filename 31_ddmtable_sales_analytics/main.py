from YoungLion import DDMTable
from models import Sale

rows = DDMTable(Sale({"id":i,"region":"AZ" if i%2 else "EU","amount":20+(i%9)*15,"quantity":1+i%4}) for i in range(200))
print("columns:", rows.columns())
print("AZ revenue:", rows.query(region="AZ").sum("amount"))
print("mean qty:", rows.mean("quantity"))
print("sample report:", rows.select("id","region","amount")[:5])
