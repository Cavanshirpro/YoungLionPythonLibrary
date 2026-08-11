from __future__ import annotations
from repository import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def demo(self):
        az_orders = self.repository.where(shipping__country="AZ", paid=True)
        pending = self.repository.where(status="pending")
        if pending:
            pending[0].mark_paid()
        return {"azerbaijan_revenue": sum(o.total for o in az_orders), "updated_status": pending[0].status if pending else None}
