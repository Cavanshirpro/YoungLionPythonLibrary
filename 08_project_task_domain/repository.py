from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import Task


class TaskRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(Task(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'priority', 'done', 'assignment.owner', 'assignment.team')

    def by_id(self, value: int) -> Task | None:
        return self.search.find_one("id", value)

    def where(self, **lookups):
        return self.search.where(**lookups)

    def refresh(self) -> None:
        self.search.refresh()

    def snapshot(self) -> list[dict]:
        return [item.to_dict() for item in self.items]
