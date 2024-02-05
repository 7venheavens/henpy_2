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
        )["props"]["pageProps"]

    def check_valid(self) -> None:
        a = True
        if not a:
            raise ValueError("Page does not contain valid data")

    @cached_property
    def id(self) -> str:
        return self.json_data["work"]["work_id"]

    @cached_property
    def title(self) -> str:
        return self.json_data["work"]["title"]

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
        cast = self.json_data["work"]["casts"]
        res = []
        for _dict in cast:
            name = _dict["actor"]["name"]
            res.append(name)
        return res

    @property
    def tags(self) -> list[tuple[str, str]]:
        """Returns a list of tuples of (tag_id, tag_name)
        Tag name can vary across time as this often gets updated
        """
        tags = self.json_data["work"]["genres"]

        return [(tag["name"], tag["name"]) for tag in tags if tag["name"]]

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
        return self.json_data["work"]["products"][0].get("image_url", "")

    @property
    def thumbnail_urls(self) -> list[str]:
        thumbnails = self.json_data["work"]["products"][0].get("sample_image_urls", [])
        res = [i.get("l", i.get("s", None)) for i in thumbnails]
        return [i for i in res if i]
