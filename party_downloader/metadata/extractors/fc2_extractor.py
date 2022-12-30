from __future__ import annotations
from party_downloader.metadata.extractors.base_metadata_extractor import (
    BaseMetadataExtractor,
)
from party_downloader.models.web_data import WebData
from functools import cached_property
from datetime import date
import re


class FC2Extractor(BaseMetadataExtractor):
    def __init__(self, webdata: WebData):
        super().__init__(webdata)
        # Soup derivatives for ease of use
        self._container = webdata.soup

    @cached_property
    def id(self) -> str:
        return (
            "FC2-PPV" + self._container.find("title").text.split("FC2-PPV")[1].strip()
        )

    @cached_property
    def title(self) -> str:
        return self._container.find("title").text.split("FC2-PPV")[0].strip()

    @property
    def producer(self) -> str:
        return (
            self._container.find(class_="items_comment_sellerBox")
            .find("h4")
            .find("a")
            .text
        )

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
    def tags(self) -> list[tuple[str, str]]:
        """Returns a list of tuples of (tag_id, tag_name)
        Tag name can vary across time as this often gets updated
        """
        tag_data = self._container.find_all("a", class_="tag")
        tags = [
            (tag["href"].split("/")[-1], tag.text.strip()) for tag in tag_data if tag
        ]
        return [
            (tag[0][5:], tag[1]) if tag[0].startswith("?tag=") else tag for tag in tags
        ]

    @property
    def release_date(self) -> date | None:
        raw_date_text = self._container.find(class_="items_article_Releasedate")
        match = re.search(r"(\d+/\d+/\d+)", raw_date_text.text)
        if not match:
            return None
        raw_date = match.group(1)
        return date.fromisoformat(raw_date.replace("/", "-"))

    @property
    def duration(self) -> int | None:
        ele = self._container.find(class_="items_article_info")
        match = re.search(r"(\d+:\d+:\d+)", ele.text)
        if not match:
            return 0
        mult = [3600, 60, 1]
        time = match.group(1).split(":")
        return sum([int(t) * m for t, m in zip(time, mult)])

    @property
    def cover_url(self) -> str:
        cover = self._container.find("div", class_="items_article_MainitemThumb").find(
            "img"
        )
        href = cover["src"]
        if not href:
            return ""
        return self.webdata.clean_url_link(href)

    @property
    def thumbnail_urls(self) -> list[str]:
        thumbs = self._container.find(class_="items_article_SampleImagesArea").find_all(
            "a"
        )
        if not thumbs:
            return []
        return [self.webdata.clean_url_link(thumb["href"]) for thumb in thumbs]
