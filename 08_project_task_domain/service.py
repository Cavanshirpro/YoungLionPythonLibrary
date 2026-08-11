from __future__ import annotations
from repository import TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def demo(self):
        mine = self.repository.where(assignment__owner="cavan", done=False)
        for task in mine: task.advance(0.25)
        return [(t.title, t.progress, t.done) for t in mine]
