from __future__ import annotations
from party_downloader.models.metadata.extractors.base_metadata_extractor import (
    BaseMetadataExtractor,
)
from party_downloader.models.web_data import WebData
from functools import cached_property
from datetime import date
import re

# maps the ones defined by columns
singleton_mapping = {
    "ID:": "id",
    "Release Date:": "release_date",
    "Length:": "length",
    "Director:": "director",
    "Studio:": "studio",
    "Label:": "label",
    "Series": "series",
    # TODO add japanese
}


class JavBusExtractor(BaseMetadataExtractor):
    def __init__(self, webdata: WebData):
        super().__init__(webdata)
        # Soup derivatives for ease of use
        self._container = webdata.soup.find("div", class_="container")
        self._info = self._container.find("div", class_="info")
        # Get the singleton data (non-list)
        holder = self._info.find_all("span", class_="header")
        self._singletons = {}
        for span in holder:
            key = span.text
            if key in singleton_mapping:
                self._singletons[singleton_mapping[key]] = span

    @cached_property
    def id(self) -> str:
        return self._singletons["id"].next_sibling.next_sibling.text.strip()

    @cached_property
    def title(self) -> str:
        return self._container.find("h3").text.strip()

    @property
    def producer(self) -> str:
        producer = self._singletons.get("director", "")
        if not producer:
            return ""
        return producer.find_next_sibling("a").text.strip()

    @property
    def publisher(self) -> str:
        publisher = self._singletons.get("studio", "")
        if not publisher:
            return ""
        return publisher.find_next_sibling("a").text.strip()

    @property
    def studio(self) -> str:
        studio = self._singletons.get("label", "")
        if not studio:
            return ""
        return studio.find_next_sibling("a").text.strip()

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
        date_element = self._singletons.get("release_date", None)
        if not date_element:
            return None
        raw_date = date_element.next_sibling.text.strip()
        if not raw_date:
            return None
        return date.fromisoformat(raw_date)

    @property
    def duration(self) -> int | None:
        duration_element = self._singletons.get("length", None)
        if not duration_element:
            return None
        raw_duration = duration_element.next_sibling.text.strip()
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
