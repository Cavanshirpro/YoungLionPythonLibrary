from YoungLion import NumericSearch
products=[(1299,{"id":1,"name":"Laptop"}),(49,{"id":2,"name":"Mouse"}),(99,{"id":3,"name":"Keyboard"}),(799,{"id":4,"name":"Office Laptop"})]
idx=NumericSearch(products)
print("range:",idx.range(50,900))
print("nearest:",idx.nearest(750,k=2))
