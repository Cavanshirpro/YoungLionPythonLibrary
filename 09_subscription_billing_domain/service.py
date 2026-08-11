from __future__ import annotations
from repository import SubscriptionRepository


class SubscriptionService:
    def __init__(self, repository: SubscriptionRepository):
        self.repository = repository

    def demo(self):
        renew_today = self.repository.where(renewal_day=12, active=True)
        return [(s.id, s.plan, s.annual_cost(), s.billing.auto_renew) for s in renew_today]
