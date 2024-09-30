from __future__ import annotations
from dataclasses import dataclass
from party_downloader.models.web_data import WebData
from datetime import date
from functools import cached_property
from xml.dom import minidom
import xml.etree.cElementTree as ET
from abc import ABC, abstractmethod


class BaseMetadataExtractor(ABC):
    """Base class for the extraction of metadata from some metadata page
    Extractors are used to extract metadata from an acquired metadata page
    """

    fields = [
        "id",
        "title",
        "description",
        "producer",
        "publisher",
        "studio",
        "series",
        "actors",
        "tags",
        "release_date",
        "duration",
        "cover_url",
        "thumbnail_urls",
    ]

    def __init__(self, webdata: WebData):
        self.webdata = webdata
        # self.check_valid()

    # @abstractmethod
    # def check_valid(self) -> bool:
    #     """Checks if the metadata page is valid and does not point to a "did not find" type age"""
    #     pass

    @staticmethod
    def get_element_text(element):
        if not element:
            return None
        res = element.text.strip()
        return res if res else None

    @property
    def id(self) -> str:
        return ""

    @property
    def title(self) -> str:
        return ""

    @property
    def description(self) -> str:
        return ""

    @property
    def producer(self) -> str:
        return ""

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
    def tags(self) -> list[tuple(str, str)]:
        """Returns a list of tuples of (tag_id, tag_name)
        Tag name can vary across time as this often gets updated
        """
        return []

    @property
    def release_date(self) -> date | None:
        return None

    @property
    def duration(self) -> int:
        "Duration in seconds"
        return 0

    @property
    def cover_url(self) -> str:
        return ""

    @property
    def background_url(self) -> str:
        return ""

    @property
    def thumbnail_urls(self) -> list[str]:
        return []

    @cached_property
    def metadata(self) -> dict:
        try:
            return {
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "producer": self.producer,
                "publisher": self.publisher,
                "studio": self.studio,
                "series": self.series,
                "actors": self.actors,
                "tags": self.tags,
                "release_date": self.release_date,
                "duration": self.duration,
                "cover_url": self.cover_url,
                "background_url": self.background_url,
                "thumbnail_urls": self.thumbnail_urls,
            }
        except:
            print(f"Failed for webdata for {self.webdata.url}")
            # print(self.webdata.soup.prettify())
            raise

    @cached_property
    def metadata_nfo(self) -> str:
        """Returns the metadata in nfo format"""
        root = ET.Element("movie")
        title = ET.SubElement(root, "title")
        title.text = self.title
        director = ET.SubElement(root, "director")
        director.text = self.producer
        studio = ET.SubElement(root, "studio")
        studio.text = self.studio
        for genre in self.tags:
            genre_tag = ET.SubElement(root, "genre")
            genre_tag.text = genre[1]
        for actor in self.actors:
            actor_tag = ET.SubElement(root, "actor")
            actor_name_tag = ET.SubElement(actor_tag, "name")
            actor_name_tag.text = actor
            actor_altname_tag = ET.SubElement(actor_tag, "altname")
            actor_altname_tag.text = actor
            actor_thumb_tag = ET.SubElement(actor_tag, "thumb")
            actor_thumb_tag.text = ""
            actor_role_tag = ET.SubElement(actor_tag, "role")
            actor_role_tag.text = "Actress"

        plot = ET.SubElement(root, "plot")
        plot.text = self.description
        id = ET.SubElement(root, "id")
        id.text = self.id
        year = ET.SubElement(root, "year")
        premiered = ET.SubElement(root, "premiered")
        if self.release_date:
            year.text = str(self.release_date.year)
            premiered.text = self.release_date.isoformat()

        dom = minidom.parseString(ET.tostring(root))
        return dom.toprettyxml(indent="  ")
