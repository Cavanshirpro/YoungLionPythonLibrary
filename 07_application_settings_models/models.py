from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class UiSettings(DDM):
    theme: str
    scale: float
    language: str

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.theme = str(data.get('theme', "dark"))
        self.scale = float(data.get('scale', 1.0))
        self.language = str(data.get('language', "en"))


class SettingsProfile(DDM):
    id: int
    name: str
    active: bool
    autosave_seconds: int
    ui: UiSettings

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.name = str(data.get('name', "Default"))
        self.active = bool(data.get('active', False))
        self.autosave_seconds = int(data.get('autosave_seconds', 30))
        self.ui = UiSettings(data.get('ui', {}))

    def activate(self) -> None:
        self.active = True

    def set_scale(self, scale: float) -> None:
        if not 0.5 <= scale <= 3.0: raise ValueError("unsupported scale")
        self.ui.scale = scale
