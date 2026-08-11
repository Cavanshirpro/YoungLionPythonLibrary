from YoungLion import PackedDDM

products = [PackedDDM({"id": i, "name": f"Product {i}", "price": i * 1.5}) for i in range(1, 6)]
print(products[2].get_path("name"))
print(products[0].memory_info())
