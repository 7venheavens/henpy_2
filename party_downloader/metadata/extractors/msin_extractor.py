from __future__ import annotations
from party_downloader.metadata.extractors.base_metadata_extractor import (
    BaseMetadataExtractor,
)
from party_downloader.models.web_data import WebData
from functools import cached_property
from datetime import date
import re


class MSINExtractor(BaseMetadataExtractor):
    def __init__(self, webdata: WebData):
        super().__init__(webdata)
        # Soup derivatives for ease of use
        self.soup = webdata.soup

    @cached_property
    def id(self) -> str:
        return self.soup.find(class_="mv_fileName").text.strip()

    @cached_property
    def title(self) -> str:
        return self.soup.find(class_="mv_title").text.strip()

    @property
    def producer(self) -> str:
        return self.soup.find(class_="mv_writer").text.strip()

    @property
    def publisher(self) -> str:
        return self.soup.find(class_="mv_mfr").text.strip()

    @property
    def studio(self) -> str:
        group = self.soup.find(class_="group_head")
        return group.text.strip() if group else ""

    @property
    def series(self) -> str:
        return ""

    @property
    def actors(self) -> list:
        performer_view = self.soup.find(class_="text", text="出演者：")
        if not performer_view:
            return []
        performer_view.find_next_sibling("div", class_="performer_view")
        res = []
        for performer_box in performer_view.find_all("div", class_="performer_box"):
            text = performer_box.find(class_="performer_text")
            performer_href = text.find("a")["href"]
            performer_name = text.find("a").text.strip()
            performer_id = performer_href.split("=")[1]
            res.append(performer_name)
        return res

    @property
    def tags(self) -> list[tuple[str, str]]:
        """Returns a list of tuples of (tag_id, tag_name)
        Tag name can vary across time as this often gets updated
        """
        tags = self.soup.find(class_="mv_tag").find_all("label")
        return [(tag.text.strip(), tag.text.strip()) for tag in tags]

    @property
    def release_date(self) -> date | None:
        raw_date = self.soup.find(class_="mv_createDate").text.strip()
        if not raw_date:
            return None
        return date.fromisoformat(raw_date)

    @property
    def duration(self) -> int | None:
        raw_duration = self.soup.find(class_="mv_duration").text.strip()
        if not raw_duration:
            return None
        try:
            hours, minutes, seconds = raw_duration.split(":")
        except ValueError:
            pass
        try:
            hours, minutes = raw_duration.split(":")
            seconds = 0
        except ValueError:
            pass
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds)

    @property
    def cover_url(self) -> str:
        movie_box = self.soup.find(class_="movie_top")
        cover = movie_box.find("img")
        href = cover["src"]
        if not href:
            return ""
        # return self.webdata.root_url + href
        return href

    @property
    def thumbnail_urls(self) -> list[str]:
        links = self.soup.find(class_="mv_com1").find_all(
            "div", class_=lambda x: x != "text" and x != "mv_coverUrl"
        )
        return [link.text.strip() for link in links]
