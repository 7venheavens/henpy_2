from __future__ import annotations
from party_downloader.metadata.extractors.base_metadata_extractor import (
    BaseMetadataExtractor,
)
from party_downloader.models.web_data import WebData
from functools import cached_property
from datetime import date
import re


class JavLibraryExtractor(BaseMetadataExtractor):
    def __init__(self, webdata: WebData):
        super().__init__(webdata)
        # Soup derivatives for ease of use
        self._info = webdata.soup.find(id="video_id")

    @cached_property
    def id(self) -> str:
        return self._info.find(id="video_id").find(class_="text").text.strip()

    @cached_property
    def title(self) -> str:
        return self.webdata.soup.find("h3", class_="post-title text").text.strip()

    @property
    def producer(self) -> str:
        return self._info.find(id="video_director").find(class_="text").text.strip()

    @property
    def publisher(self) -> str:
        return self._info.find(id="video_maker").find(class_="text").text.strip()

    @property
    def studio(self) -> str:
        return self._info.find(id="video_label").find(class_="text").text.strip()

    @property
    def series(self) -> str:
        series = self._singletons.get("series", "")
        if not series:
            return ""
        return series.find_next_sibling("a").text.strip()

    @property
    def actors(self) -> list:
        tag_data = self._info.find_all("span", class_="star-name")
        return [tag.text.strip() for tag in tag_data]

    @property
    def tags(self) -> list[tuple[str, str]]:
        """Returns a list of tuples of (tag_id, tag_name)
        Tag name can vary across time as this often gets updated
        """
        tag_data = (
            self._info.find(id="genre-toggle")
            .parent.find_next_sibling("p")
            .find_all("span", class_="genre")
        )
        tag_data = [tag.find("a") for tag in tag_data]
        return [
            (tag["href"].split("/")[-1], tag.text.strip()) for tag in tag_data if tag
        ]

    @property
    def release_date(self) -> date | None:
        raw_date = self._info.find(id="video_date").find(class_="text").text.strip()
        if not raw_date:
            return None
        return date.fromisoformat(raw_date)

    @property
    def duration(self) -> int | None:
        raw_duration = (
            self._info.find(id="video_length").find(class_="text").text.strip()
        )
        if not raw_duration:
            return None
        return int(re.sub("[^0-9]", "", raw_duration))

    @property
    def cover_url(self) -> str:
        cover = self._container.find("div", class_="screencap").find("a")
        href = cover["href"]
        if not href:
            return ""
        return self.webdata.root_url + href

    @property
    def thumbnail_urls(self) -> list[str]:
        thumbs = self._container.find_all("a", class_="sample-box")
        if not thumbs:
            return []
        return [thumb["href"] for thumb in thumbs]
