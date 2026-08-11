from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class UserProfile(DDM):
    display_name: str
    country: str
    age: int

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.display_name = str(data.get('display_name', "Unknown"))
        self.country = str(data.get('country', "Unknown"))
        self.age = int(data.get('age', 0))


class User(DDM):
    id: int
    username: str
    role: str
    active: bool
    profile: UserProfile

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.username = str(data.get('username', "unknown"))
        self.role = str(data.get('role', "member"))
        self.active = bool(data.get('active', True))
        self.profile = UserProfile(data.get('profile', {}))

    def can_access_admin(self) -> bool:
        return self.active and self.role == "admin"

    def rename(self, username: str) -> None:
        username = username.strip()
        if len(username) < 3:
            raise ValueError("username is too short")
        self.username = username
