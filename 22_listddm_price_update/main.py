from YoungLion import ListDDM

products = ListDDM({"sku": f"P{i}", "price": 10 + i} for i in range(10))
products.multiply("price", 1.10)
products.clamp("price", 0, 18)
print([p.to_dict() for p in products.top("price", 3)])
