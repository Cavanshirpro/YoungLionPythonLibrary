from __future__ import annotations
from repository import ApiUserRepository


class ApiUserService:
    def __init__(self, repository: ApiUserRepository):
        self.repository = repository

    def demo(self):
        active = self.repository.where(status="active")
        return {"active": [u.public_view() for u in active], "unknown_field_preserved": self.repository.items[0].get("new_server_field")}
