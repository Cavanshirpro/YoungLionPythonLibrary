from YoungLion import Dataset

data = Dataset(rows=[
    {"region": "AZ", "revenue": 120.0},
    {"region": "TR", "revenue": 180.0},
    {"region": "AZ", "revenue": 90.0},
])
print("Revenue stats:", data.stats("revenue"))
print("Regions:", {k: len(v.rows) for k, v in data.group_by("region").items()})
