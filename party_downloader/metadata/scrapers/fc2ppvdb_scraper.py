from __future__ import annotations
from party_downloader.metadata.scrapers.base_metadata_scraper import BaseMetadataScraper
from pathlib import Path
from party_downloader.models.web_data import WebData
from party_downloader.helpers import Regexes
import re

FC2_REGEX = re.compile(r"fc2-ppv-(\d+)", re.IGNORECASE)


class FC2PPVDBScraper(BaseMetadataScraper):
    COMPONENT_REGEX = Regexes.FC2
    SEARCH_TEMPLATE = "https://www.fc2ppvdb.com/search?stype=title&keyword={}"

    @classmethod
    def get_id_components(cls, file: str | Path) -> tuple[str, str] | None:
        print(file)
        res = super().get_id_components(cls, file)
        if res:
            res["name"] = f'fc2-ppv-{res["id"]}'
        return res

    def is_valid(self, webdata: WebData):
        if webdata.soup.find(text=re.compile("Search Result For: ")):
            raise ValueError("No results found")

    def search(self, query: str) -> WebData:
        return super().search(query)
