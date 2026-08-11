from service import Catalog
rows=[{"id":1,"name":"Gaming Laptop","description":"RTX graphics fast gaming notebook","category":"computer","price":1299,"stock":4},{"id":2,"name":"Office Laptop","description":"quiet productivity notebook","category":"computer","price":799,"stock":10},{"id":3,"name":"Wireless Mouse","description":"ergonomic bluetooth mouse","category":"accessory","price":49,"stock":0}]
c=Catalog(rows)
print([p.name for p in c.search("gming laptp")])
print([p.name for p in c.available_under("computer",1000)])
