from __future__ import annotations
from party_downloader.metadata.extractors.base_metadata_extractor import (
    BaseMetadataExtractor,
)
from party_downloader.models.web_data import WebData
from functools import cached_property
from datetime import date
import re


class FC2PPVDBExtractor(BaseMetadataExtractor):
    def __init__(self, webdata: WebData):
        super().__init__(webdata)
        # Soup derivatives for ease of use
        self._container = webdata.soup

    def check_valid(self) -> None:
        a = True
        if not a:
            raise ValueError("Page does not contain valid data")

    def _get_value(self, element) -> str:
        if not element:
            return ""
        return element.find_next("span").text.strip()

    @cached_property
    def id(self) -> str:
        return "FC2-PPV-" + self._get_value(self._container.find(text="ID："))

    @cached_property
    def title(self) -> str:
        return self._container.find("title").text.split("- FC2PPVDB")[0].strip()

    @property
    def producer(self) -> str:
        return self._get_value(self._container.find(text="販売者："))

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
        actor = self._get_value(self._container.find(text="女優："))
        if actor:
            return [actor]
        return []

    @property
    def tags(self) -> list[tuple[str, str]]:
        """Returns a list of tuples of (tag_id, tag_name)
        Tag name can vary across time as this often gets updated
        """
        mosaic = self._get_value(self._container.find(text="モザイク："))
        tag_data = self._container.find(text="タグ：").find_next("span").find_all("a")

        raw_tags = [(tag["href"].split("?name=")[-1]) for tag in tag_data if tag]
        tags = [(tag, tag) for tag in raw_tags]
        if mosaic == "無":
            tags.append(("uncensored", "uncensored"))
        return tags

    @property
    def release_date(self) -> date | None:
        raw_date_text = self._get_value(self._container.find(text="販売日："))
        match = re.search(r"(\d+-\d+-\d+)", raw_date_text)
        if not match:
            return None
        raw_date = match.group(1)
        return date.fromisoformat(raw_date.replace("/", "-"))

    @property
    def duration(self) -> int | None:
        ele = self._get_value(self._container.find(text="収録時間："))
        match = re.search(r"(\d+:\d+)", ele)
        if not match:
            return 0
        mult = [3600, 60, 1]
        time = match.group(1).split(":")
        if len(time) == 2:
            time = ["0"] + time
        return sum([int(t) * m for t, m in zip(time, mult)])

    @property
    def cover_url(self) -> str:
        cover = self._container.find("img", class_="object-contain")
        href = cover["src"]
        if not href:
            return ""
        return self.webdata.clean_url_link(href)

    @property
    def thumbnail_urls(self) -> list[str]:
        return []
