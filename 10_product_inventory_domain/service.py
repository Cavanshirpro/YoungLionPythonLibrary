from __future__ import annotations
from repository import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def demo(self):
        empty = self.repository.where(stock=0)
        for product in empty: product.restock(10)
        self.repository.refresh()
        return {p.sku: p.stock_value() for p in self.repository.items}
