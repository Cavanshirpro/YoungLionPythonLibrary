from __future__ import annotations
from repository import MediaItemRepository


class MediaItemService:
    def __init__(self, repository: MediaItemRepository):
        self.repository = repository

    def demo(self):
        videos = self.repository.where(kind="video", rating__ge=4)
        return [(m.title, m.media.codec, m.is_4k()) for m in videos]
