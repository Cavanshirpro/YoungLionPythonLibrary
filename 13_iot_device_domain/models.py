from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class Telemetry(DDM):
    temperature: float
    voltage: float
    signal: int

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.temperature = float(data.get('temperature', 0.0))
        self.voltage = float(data.get('voltage', 0.0))
        self.signal = int(data.get('signal', 0))


class Device(DDM):
    id: int
    name: str
    site: str
    online: bool
    firmware: str
    telemetry: Telemetry

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.name = str(data.get('name', ""))
        self.site = str(data.get('site', ""))
        self.online = bool(data.get('online', False))
        self.firmware = str(data.get('firmware', ""))
        self.telemetry = Telemetry(data.get('telemetry', {}))

    def healthy(self) -> bool:
        return self.online and 2.8 <= self.telemetry.voltage <= 3.4 and self.telemetry.temperature < 60

    def update_firmware(self, version: str) -> None:
        self.firmware = version
