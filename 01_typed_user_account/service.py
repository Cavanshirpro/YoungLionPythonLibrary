from __future__ import annotations
from repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def demo(self):
        user = self.repository.by_id(2)
        assert user is not None
        user.rename("cavanshir")
        adults = self.repository.where(profile__age__ge=18, active=True)
        self.repository.refresh()
        return {"renamed": user.username, "adult_active_ids": [u.id for u in adults]}
