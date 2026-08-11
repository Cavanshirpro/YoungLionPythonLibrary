from __future__ import annotations
from repository import StudentRepository


class StudentService:
    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def demo(self):
        cs = self.repository.where(academic__program="CS", active=True)
        honors = [s.name for s in self.repository.items if s.honor_candidate()]
        return {"active_cs": [s.name for s in cs], "honors": honors}
