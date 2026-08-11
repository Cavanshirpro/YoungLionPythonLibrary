from YoungLion import ListDDM, DDM

products = ListDDM(DDM({"id":i,"stock":i%8,"price":10+(i%25)}) for i in range(1000))
empty,available = products.partition_path("stock",0,op="eq")
restock = ListDDM(empty)
restock.set_all("stock",25)
print("restocked:", len(restock), "available before:",len(available))
print("stock total:", products.sum("stock"))
