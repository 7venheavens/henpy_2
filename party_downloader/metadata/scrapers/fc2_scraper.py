from __future__ import annotations
from party_downloader.metadata.scrapers.base_metadata_scraper import BaseMetadataScraper
from pathlib import Path
from party_downloader.models.web_data import WebData
from party_downloader.helpers import Regexes
import re

FC2_REGEX = re.compile(r"fc2-ppv-(\d+)", re.IGNORECASE)


class FC2Scraper(BaseMetadataScraper):
    COMPONENT_REGEX = Regexes.FC2
    SEARCH_TEMPLATE = "https://adult.contents.fc2.com/article/{id_num}/"

    @classmethod
    def get_id_components(cls, file: str | Path) -> tuple[str, str] | None:
        res = super().get_id_components(file)
        if res:
            res["name"] = f'fc2-ppv-{res["id"]}'
        return res

    def is_valid(self, webdata: WebData):
        if webdata.soup.find(class_="items_notfound_wp"):
            raise ValueError("Invalid data")

    def search(self, query: str) -> WebData:
        res = WebData(self.SEARCH_TEMPLATE_TEMPLATE.format(id_num=query))
        self.is_valid(res)
        return res
