from YoungLion import DDM
class Product(DDM):
    def __init__(self,d): super().__init__(d); self.id=int(d.get("id",0)); self.name=str(d.get("name","")); self.description=str(d.get("description","")); self.category=str(d.get("category","")); self.price=float(d.get("price",0)); self.stock=int(d.get("stock",0))
