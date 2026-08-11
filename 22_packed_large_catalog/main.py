from YoungLion import PackedDDM

rows = [PackedDDM({"id": i, "sku": f"SKU-{i:06d}", "price": (i % 200) + 0.99}) for i in range(10000)]
print("records:", len(rows))
print("sample:", rows[4321].to_dict())
print("sample memory:", rows[4321].memory_info())
