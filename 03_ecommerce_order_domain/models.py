from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class Shipping(DDM):
    country: str
    city: str
    method: str

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.country = str(data.get('country', ""))
        self.city = str(data.get('city', ""))
        self.method = str(data.get('method', "standard"))


class Order(DDM):
    id: int
    status: str
    subtotal: float
    shipping_cost: float
    paid: bool
    shipping: Shipping

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.status = str(data.get('status', "pending"))
        self.subtotal = float(data.get('subtotal', 0.0))
        self.shipping_cost = float(data.get('shipping_cost', 0.0))
        self.paid = bool(data.get('paid', False))
        self.shipping = Shipping(data.get('shipping', {}))

    @property
    def total(self) -> float:
        return round(self.subtotal + self.shipping_cost, 2)

    def mark_paid(self) -> None:
        self.paid = True
        if self.status == "pending":
            self.status = "processing"
