from __future__ import annotations
from repository import DeviceRepository


class DeviceService:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository

    def demo(self):
        lab = self.repository.where(site="lab", online=True)
        return {d.name: d.healthy() for d in lab}
