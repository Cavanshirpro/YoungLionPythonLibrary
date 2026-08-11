from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class BillingProfile(DDM):
    method: str
    country: str
    auto_renew: bool

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.method = str(data.get('method', "card"))
        self.country = str(data.get('country', "AZ"))
        self.auto_renew = bool(data.get('auto_renew', True))


class Subscription(DDM):
    id: int
    plan: str
    monthly_price: float
    renewal_day: int
    active: bool
    billing: BillingProfile

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.plan = str(data.get('plan', "free"))
        self.monthly_price = float(data.get('monthly_price', 0.0))
        self.renewal_day = int(data.get('renewal_day', 1))
        self.active = bool(data.get('active', True))
        self.billing = BillingProfile(data.get('billing', {}))

    def cancel(self) -> None:
        self.active = False
        self.billing.auto_renew = False

    def annual_cost(self) -> float:
        return round(self.monthly_price * 12, 2)
