from __future__ import annotations
from repository import AuditEventRepository


class AuditEventService:
    def __init__(self, repository: AuditEventRepository):
        self.repository = repository

    def demo(self):
        important = self.repository.where(severity__ge=4)
        return [e.summary() for e in important if e.security_relevant()]
