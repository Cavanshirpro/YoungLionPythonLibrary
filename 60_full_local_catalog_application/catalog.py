from pathlib import Path

from YoungLion import ListDDM, DDMSearchEngine, ApplicationSearch, File, Logger
from models import Product
class CatalogApp:
    def __init__(self,root,rows):
        self.files=File(root); self.log=Logger(str(Path(root) / "catalog.log"),console=False,max_bytes=100000,backup_count=2); self.products=ListDDM(Product(x) for x in rows); self.paths=self.products.indexed("id","category","price","stock","supplier.country"); self.text=ApplicationSearch(); self._rebuild_text()
    def _rebuild_text(self):
        self.text=ApplicationSearch()
        for p in self.products: self.text.add(p.id,title=p.name,body=p.description,tags=[p.category,p.supplier.name],fields={"category":p.category,"country":p.supplier.country},payload=p)
    def query(self,text,category=None,max_price=None):
        candidates=self.text.search(text,limit=50); allowed={id(p) for p in candidates}
        if category: allowed &= {id(p) for p in self.paths.find("category",category)}
        if max_price is not None: allowed &= {id(p) for p in self.paths.find("price",max_price,op="le")}
        return [p for p in candidates if id(p) in allowed]
    def restock_empty(self,amount=10):
        empty=self.paths.find("stock",0); [p.restock(amount) for p in empty]; self.paths.refresh(); self._rebuild_text(); self.log.info("restocked",count=len(empty),amount=amount); return len(empty)
    def save(self): self.files.atomic_write_json("catalog.json",[p.to_dict() for p in self.products]); return self.files.checksum("catalog.json")
