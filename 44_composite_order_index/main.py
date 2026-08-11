from YoungLion import ListDDM, DDMSearchEngine
from models import Order
orders=ListDDM(Order({"id":i,"tenant":f"t{i%5}","status":["pending","paid","shipped"][i%3],"total":10+i%500,"customer":{"country":["AZ","US","DE"][i%3],"tier":"pro" if i%4==0 else "free"}}) for i in range(30000))
engine=DDMSearchEngine(orders)
engine.create_composite_index("tenant","status","customer.country")
rows=engine.composite(("tenant","status","customer.country"),("t2","shipped","DE"))
print("matches:",len(rows),"sample:",rows[0].to_dict() if rows else None)
