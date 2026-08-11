from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class ApiMeta(DDM):
    request_id: str
    page: int
    cached: bool

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.request_id = str(data.get('request_id', ""))
        self.page = int(data.get('page', 1))
        self.cached = bool(data.get('cached', False))


class ApiUser(DDM):
    id: int
    email: str
    status: str
    verified: bool
    meta: ApiMeta

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.email = str(data.get('email', ""))
        self.status = str(data.get('status', "unknown"))
        self.verified = bool(data.get('verified', False))
        self.meta = ApiMeta(data.get('meta', {}))

    def public_view(self) -> dict[str, object]:
        return {"id": self.id, "email": self.email, "status": self.status, "verified": self.verified}

    def activate(self) -> None:
        if not self.verified: raise RuntimeError("verification required")
        self.status = "active"
