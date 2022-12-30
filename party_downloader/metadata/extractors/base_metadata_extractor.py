from __future__ import annotations
from dataclasses import dataclass
from party_downloader.models.web_data import WebData
from datetime import date
from functools import cached_property


class BaseMetadataExtractor:
    """Base class for the extraction of metadata from some metadata page"""

    def __init__(self, webdata: WebData):
        self.webdata = webdata

    @property
    def id(self) -> str:
        return ""

    @property
    def title(self) -> str:
        return ""

    @property
    def description(self) -> str:
        return ""

    @property
    def producer(self) -> str:
        return ""

    @property
    def publisher(self) -> str:
        return ""

    @property
    def studio(self) -> str:
        return ""

    @property
    def series(self) -> str:
        return ""

    @property
    def actors(self) -> list:
        return []

    @property
    def tags(self) -> list[tuple(str, str)]:
        """Returns a list of tuples of (tag_id, tag_name)
        Tag name can vary across time as this often gets updated
        """
        return []

    @property
    def release_date(self) -> date | None:
        return None

    @property
    def duration(self) -> int:
        "Duration in seconds"
        return 0

    @property
    def cover_url(self) -> str:
        return ""

    @property
    def thumbnail_urls(self) -> list[str]:
        return []

    @cached_property
    def metadata(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "producer": self.producer,
            "publisher": self.publisher,
            "studio": self.studio,
            "series": self.series,
            "actors": self.actors,
            "tags": self.tags,
            "release_date": self.release_date,
            "duration": self.duration,
            "cover_url": self.cover_url,
            "thumbnail_urls": self.thumbnail_urls,
        }
