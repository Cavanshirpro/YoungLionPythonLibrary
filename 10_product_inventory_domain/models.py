from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class Supplier(DDM):
    id: int
    name: str
    country: str

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.name = str(data.get('name', ""))
        self.country = str(data.get('country', ""))


class Product(DDM):
    id: int
    sku: str
    name: str
    price: float
    stock: int
    supplier: Supplier

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.sku = str(data.get('sku', ""))
        self.name = str(data.get('name', ""))
        self.price = float(data.get('price', 0.0))
        self.stock = int(data.get('stock', 0))
        self.supplier = Supplier(data.get('supplier', {}))

    def restock(self, quantity: int) -> None:
        if quantity <= 0: raise ValueError("quantity must be positive")
        self.stock += quantity

    def stock_value(self) -> float:
        return round(self.price * self.stock, 2)
