from YoungLion import DDMTable

inventory = DDMTable([
    {"sku": "A", "category": "cpu", "stock": 5},
    {"sku": "B", "category": "gpu", "stock": 2},
    {"sku": "C", "category": "cpu", "stock": 9},
])
print(inventory.columns())
print(inventory.query(category="cpu").select("sku", "stock"))
