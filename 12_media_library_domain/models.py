from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class MediaInfo(DDM):
    codec: str
    width: int
    height: int
    duration: float

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.codec = str(data.get('codec', ""))
        self.width = int(data.get('width', 0))
        self.height = int(data.get('height', 0))
        self.duration = float(data.get('duration', 0.0))


class MediaItem(DDM):
    id: int
    title: str
    kind: str
    favorite: bool
    rating: int
    media: MediaInfo

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.title = str(data.get('title', ""))
        self.kind = str(data.get('kind', "video"))
        self.favorite = bool(data.get('favorite', False))
        self.rating = int(data.get('rating', 0))
        self.media = MediaInfo(data.get('media', {}))

    def is_4k(self) -> bool:
        return self.media.width >= 3840 and self.media.height >= 2160

    def favorite_it(self) -> None:
        self.favorite = True
