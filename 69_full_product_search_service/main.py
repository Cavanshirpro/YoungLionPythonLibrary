from pathlib import Path
from YoungLion import DDMTable, DDMSearchEngine, ApplicationSearch, File

products = DDMTable([
    {"id": 1, "name": "Gaming Laptop", "category": "computer", "price": 1299.0},
    {"id": 2, "name": "Office Laptop", "category": "computer", "price": 799.0},
    {"id": 3, "name": "Wireless Mouse", "category": "accessory", "price": 49.0},
])
path_index = DDMSearchEngine(products).create_indexes("category", "price")
print("Computers:", [p.name for p in path_index.find("category", "computer")])

search = ApplicationSearch()
for p in products:
    search.add(p.id, p.name, fields={"category": p.category}, payload=p)
print("Text result:", [p.name for p in search.search("gming laptp")])

File(str(Path(__file__).parent / "workspace")).atomic_write_json("catalog.json", [p.to_dict() for p in products])
