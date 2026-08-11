from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import AuditEvent


class AuditEventRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(AuditEvent(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'event_type', 'severity', 'success', 'actor.country', 'actor.id')

    def by_id(self, value: int) -> AuditEvent | None:
        return self.search.find_one("id", value)

    def where(self, **lookups):
        return self.search.where(**lookups)

    def refresh(self) -> None:
        self.search.refresh()

    def snapshot(self) -> list[dict]:
        return [item.to_dict() for item in self.items]
