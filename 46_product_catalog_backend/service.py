from YoungLion import ListDDM, DDMSearchEngine, ApplicationSearch
from models import Product
class Catalog:
    def __init__(self,rows):
        self.items=ListDDM(Product(x) for x in rows); self.structured=self.items.indexed("category","price","stock"); self.text=ApplicationSearch()
        for p in self.items: self.text.add(p.id,title=p.name,body=p.description,fields={"category":p.category},payload=p)
    def search(self,q): return self.text.search(q,limit=5)
    def available_under(self,category,price): return [p for p in self.structured.find("category",category) if p.price<=price and p.stock>0]
