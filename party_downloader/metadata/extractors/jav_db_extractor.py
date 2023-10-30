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


class JavDBExtractor(BaseMetadataExtractor):
    def __init__(self, webdata: WebData):
        super().__init__(webdata)
        # Soup derivatives for ease of use
        self.panels = webdata.soup.find_all(class_="panel-block")
        self.panel_data = dict(
            self._unpack_panel(panel) for panel in self.panels if panel
        )

    def _unpack_panel(self, panel):
        key, val = panel.find("strong"), panel.find("span")
        if key:
            return key.text, val
        return None, None

    @cached_property
    def id(self) -> str:
        return self.panel_data["ID:"].text.strip()

    @cached_property
    def title(self) -> str:
        title = self.webdata.soup.find(class_="current-title").text
        title = clean_text(title)
        return title

    @property
    def producer(self) -> str:
        producer = self.panel_data.get("Director:")
        if not producer:
            return ""
        producer = clean_text(producer.text)
        return producer

    @property
    def publisher(self) -> str:
        publisher = self.panel_data.get("Maker:")
        if not publisher:
            return ""
        publisher = publisher.text.strip()
        return publisher

    @property
    def studio(self) -> str:
        return ""

    @property
    def series(self) -> str:
        series = self.panel_data["Series:"].text.strip()
        return series

    @property
    def actors(self) -> list:
        tag_data = self.panel_data["Actor(s):"].find_all("a")
        actors = [i.text.strip() for i in tag_data]
        return actors

    @property
    def tags(self) -> list[tuple[str, str]]:
        """Returns a list of tuples of (tag_id, tag_name)
        Tag name can vary across time as this often gets updated
        """
        tag_data = self.panel_data["Tags:"].find_all("a")
        return [
            (tag["href"].split("?")[-1], clean_text(tag.text))
            for tag in tag_data
            if tag
        ]

    @property
    def release_date(self) -> date | None:
        raw_date = self.panel_data["Released Date:"].text.strip()
        if not raw_date:
            return None
        return date.fromisoformat(raw_date)

    # @property
    # def duration(self) -> int | None:
    #     raw_duration = self.panel_data["Duration:"].text.strip()
    #     if not raw_duration:
    #         return None
    #     return int(re.sub("[^0-9]", "", raw_duration))

    @property
    def cover_url(self) -> str:
        href = self.webdata.soup.find(class_="column-video-cover").find("img")["src"]
        if not href:
            return ""
        if not href.startswith("http"):
            return "https:" + href
        return href

    @property
    def thumbnail_urls(self) -> list[str]:
        thumbs = self.webdata.soup.find(class_="preview-images")
        if not thumbs:
            return []
        thumbs = thumbs.find_all("a")
        if not thumbs:
            return []
        return [thumb["href"] for thumb in thumbs]
