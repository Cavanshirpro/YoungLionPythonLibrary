from tempfile import TemporaryDirectory
from catalog import CatalogApp
rows=[
 {"id":1,"name":"Gaming Laptop","description":"high performance RTX gaming notebook","category":"computer","price":1299,"stock":3,"supplier":{"name":"TechCo","country":"US"}},
 {"id":2,"name":"Office Laptop","description":"quiet efficient work notebook","category":"computer","price":799,"stock":0,"supplier":{"name":"TechCo","country":"US"}},
 {"id":3,"name":"Mechanical Keyboard","description":"hot swap tactile keyboard","category":"accessory","price":119,"stock":8,"supplier":{"name":"InputLab","country":"DE"}},
]
with TemporaryDirectory() as tmp:
    app=CatalogApp(tmp,rows)
    print("search",[(p.name,p.price) for p in app.query("ofice laptp",category="computer",max_price=1000)])
    print("restocked",app.restock_empty())
    print("digest",app.save())
    print("stats",app.paths.stats())
