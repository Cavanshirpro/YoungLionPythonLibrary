from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class Owner(DDM):
    name: str
    country: str
    verified: bool

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.name = str(data.get('name', ""))
        self.country = str(data.get('country', ""))
        self.verified = bool(data.get('verified', False))


class BankAccount(DDM):
    id: int
    currency: str
    balance: float
    locked: bool
    owner: Owner

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.currency = str(data.get('currency', "USD"))
        self.balance = float(data.get('balance', 0.0))
        self.locked = bool(data.get('locked', False))
        self.owner = Owner(data.get('owner', {}))

    def deposit(self, amount: float) -> None:
        if amount <= 0: raise ValueError("amount must be positive")
        if self.locked: raise RuntimeError("account is locked")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0: raise ValueError("amount must be positive")
        if self.locked or amount > self.balance: raise RuntimeError("withdrawal denied")
        self.balance -= amount
