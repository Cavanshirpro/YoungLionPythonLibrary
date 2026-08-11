from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class AcademicProfile(DDM):
    program: str
    year: int
    gpa: float

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.program = str(data.get('program', ""))
        self.year = int(data.get('year', 1))
        self.gpa = float(data.get('gpa', 0.0))


class Student(DDM):
    id: int
    name: str
    active: bool
    credits: int
    academic: AcademicProfile

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.name = str(data.get('name', ""))
        self.active = bool(data.get('active', True))
        self.credits = int(data.get('credits', 0))
        self.academic = AcademicProfile(data.get('academic', {}))

    def honor_candidate(self) -> bool:
        return self.active and self.academic.gpa >= 3.7

    def add_credits(self, amount: int) -> None:
        self.credits += max(0, amount)
