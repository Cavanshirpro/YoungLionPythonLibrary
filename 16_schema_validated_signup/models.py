from collections.abc import Mapping
from typing import Any
from YoungLion import DDM, SchemaDDM

SIGNUP_SCHEMA = {
    "username": {"type": str, "required": True},
    "age": {"type": int, "required": True},
    "email": {"type": str, "required": True},
}

class User(DDM):
    username: str
    age: int
    email: str
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.username = str(data.get("username", "")).strip()
        self.age = int(data.get("age", 0))
        self.email = str(data.get("email", "")).strip().casefold()
        if len(self.username) < 3: raise ValueError("username too short")

def validate_signup(data: dict) -> dict:
    result = SchemaDDM(data, SIGNUP_SCHEMA)
    return result.to_dict()
