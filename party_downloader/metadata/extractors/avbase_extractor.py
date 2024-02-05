from __future__ import annotations
from party_downloader.metadata.extractors.base_metadata_extractor import (
    BaseMetadataExtractor,
)
from party_downloader.models.web_data import WebData
from functools import cached_property
from datetime import date
import re
from json import loads


class AVBaseExtractor(BaseMetadataExtractor):
    def __init__(self, webdata: WebData):
        super().__init__(webdata)
        # Soup derivatives for ease of use
        self._container = webdata.soup
        self.overview = self._container.find(
            class_="container mx-auto grid md:grid-cols-mainWithRight gap-4"
        )
        # get the eelemtn: <script id="__NEXT_DATA__" type="application/json">
        self.json_data = loads(
            self._container.find(
                "script", id="__NEXT_DATA__", type="application/json"
            ).text
        )

    def check_valid(self) -> None:
        a = True
        if not a:
            raise ValueError("Page does not contain valid data")

    @cached_property
    def id(self) -> str:
        return self._container.find("title").text.split(":")[0].strip()

    @cached_property
    def title(self) -> str:
        return self._container.find("h1").text

    @property
    def producer(self) -> str:
        ele = self._container.find(string="メーカー")
        if ele:
            return ele.parent.find_next_sibling().text
        return ""

    @property
    def publisher(self) -> str:
        ele = self._container.find(string="レーベル")
        if ele:
            return ele.parent.find_next_sibling().text
        return ""

    @property
    def studio(self) -> str:
        return ""

    @property
    def series(self) -> str:
        return ""

    @property
    def actors(self) -> list:
        container = self._container.find(string="出演者・メモ")
        if not container:
            return []

        actor_tags = container.parent.parent.find_all("a")
        return [actor.find("span").text for actor in actor_tags]

    @property
    def tags(self) -> list[tuple[str, str]]:
        """Returns a list of tuples of (tag_id, tag_name)
        Tag name can vary across time as this often gets updated
        """
        container = self._container.find(string="タグ・説明文")
        tags = container.parent.parent.find_next_sibling().find_all("a")

        return [(tag["href"].split("/")[-1], tag.text.strip()) for tag in tags if tag]

    @property
    def release_date(self) -> date | None:
        ele = self._container.find(string="発売日")
        if ele:
            raw_date_text = ele.parent.find_next_sibling().text
        match = re.search(r"(\d+/\d+/\d+)", raw_date_text)
        if not match:
            return None
        raw_date = match.group(1)
        return date.fromisoformat(raw_date.replace("/", "-"))

    @property
    def duration(self) -> int | None:
        ele = self._container.find(string="収録分数")
        if ele:
            ele = ele.parent.find_next_sibling()
            return int(ele.text) * 60

    @property
    def cover_url(self) -> str:
        cover = self._container.find("img")
        href = cover["src"]
        if not href:
            return ""
        return self.webdata.clean_url_link(href)

    @property
    def thumbnail_urls(self) -> list[str]:
        container = self._container.find(
            _class="w-full bg-base-300 md:basis-64 flex flex-col"
        )
        raise
        if not container:
            return []
        thumb_container = container.find_next_sibling()
        thumbs = thumb_container.find_all("a")
        if not thumbs:
            return []
        return [self.webdata.clean_url_link(thumb["href"]) for thumb in thumbs]
