from __future__ import annotations
from party_downloader.metadata.extractors.base_metadata_extractor import (
    BaseMetadataExtractor,
)
from party_downloader.models.web_data import WebData
from functools import cached_property
from datetime import date
import re


def clean_text(text):
    text = text.strip()
    return text.replace("\t", "").replace("\n", " ").strip()


class JavLibraryExtractor(BaseMetadataExtractor):
    def __init__(self, webdata: WebData):
        super().__init__(webdata)
        # Soup derivatives for ease of use
        self._info = webdata.soup.find(id="video_info")

    @cached_property
    def id(self) -> str:
        return self._info.find(id="video_id").find(class_="text").text.strip()

    @cached_property
    def title(self) -> str:
        title = self.webdata.soup.find("h3", class_="post-title text").text.strip()
        title = clean_text(title)
        return title

    @property
    def producer(self) -> str:
        producer = self._info.find(id="video_director").find(class_="text").text.strip()
        if producer == "----":
            return ""
        return producer

    @property
    def publisher(self) -> str:
        return ""

    @property
    def studio(self) -> str:
        studio = self._info.find(id="video_maker").find(class_="text").text.strip()
        if studio == "----":
            return ""
        return studio

    @property
    def series(self) -> str:
        series = self._info.find(id="video_label").find(class_="text").text.strip()
        if series == "----":
            return ""
        return series

    @property
    def actors(self) -> list:
        tag_data = self.webdata.soup.find(id="video_cast").find_all(
            "span", class_="star"
        )
        actors = [i.find("a").text.strip() for i in tag_data]
        return actors

    @property
    def tags(self) -> list[tuple[str, str]]:
        """Returns a list of tuples of (tag_id, tag_name)
        Tag name can vary across time as this often gets updated
        """
        tag_data = self._info.find(id="video_genres").find_all("span", class_="genre")
        tag_data = [tag.find("a") for tag in tag_data]
        return [
            (tag["href"].split("g=")[-1], clean_text(tag.text))
            for tag in tag_data
            if tag
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
    def background_url(self) -> str:
        href = self.webdata.soup.find(id="video_jacket_img")["src"]

        if not href:
            return ""
        # return self.webdata.root_url + href
        return "https:" + href

    @property
    def thumbnail_urls(self) -> list[str]:
        thumbs = self.webdata.soup.find(class_="previewthumbs")
        if not thumbs:
            return
        thumbs = thumbs.find_all("img")
        thumbs = [thumb for thumb in thumbs if thumb["src"] != "../img/player.gif"]
        if not thumbs:
            return []
        return [thumb["src"] for thumb in thumbs]
