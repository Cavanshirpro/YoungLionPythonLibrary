from __future__ import annotations
from repository import BankAccountRepository


class BankAccountService:
    def __init__(self, repository: BankAccountRepository):
        self.repository = repository

    def demo(self):
        verified = self.repository.where(owner__verified=True, locked=False)
        verified[0].deposit(125)
        return {a.id: a.balance for a in verified}
