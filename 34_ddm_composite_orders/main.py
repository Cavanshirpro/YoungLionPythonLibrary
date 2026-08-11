from YoungLion import ListDDM, DDMSearchEngine

orders = ListDDM([
    {"id": 1, "country": "AZ", "status": "paid"},
    {"id": 2, "country": "TR", "status": "paid"},
    {"id": 3, "country": "AZ", "status": "pending"},
])
engine = DDMSearchEngine(orders)
engine.create_composite_index("country", "status")
print([o.id for o in engine.composite(("country", "status"), ("AZ", "paid"))])
