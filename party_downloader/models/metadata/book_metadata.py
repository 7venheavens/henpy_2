from __future__ import annotations
from dataclasses import dataclass
from party_downloader.models.metadata.raw_tag import RawTag
from typing import Literal


@dataclass
class BookMetadata:
    title: str
    other_titles: list
    type: Literal["manga", "novel", "light_novel", "web_novel", "other"]
    region: str
    tags: list[RawTag]
    cover_url: str
    publisher: str
    author: list[str]
    artists: list[str]
    publisher: str
    n_volumes: int
    is_complete: bool
