from __future__ import annotations
from repository import SettingsProfileRepository


class SettingsProfileService:
    def __init__(self, repository: SettingsProfileRepository):
        self.repository = repository

    def demo(self):
        current = self.repository.search.find_one("active", True)
        assert current is not None
        current.set_scale(1.15)
        return current.to_dict()
