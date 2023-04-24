from __future__ import annotations
from party_downloader.metadata.dumpers.base_metadata_dumper import BaseMetadataDumper
from party_downloader.metadata.scrapers.base_metadata_scraper import BaseMetadataScraper
from party_downloader.models.web_data import WebData
from pathlib import Path
from party_downloader.helpers import Regexes


class MSINScraper(BaseMetadataScraper):
    COMPONENT_REGEX = Regexes.FC2
    SEARCH_TEMPLATE = "https://db.msin.jp/branch/search?sort=movie&str={id_num}"

    @classmethod
    def get_id_components(cls, file: str | Path) -> tuple[str, str] | None:
        res = super().get_id_components(file)
        if res:
            res["name"] = f'fc2-ppv-{res["id"]}'
        return res

    def is_valid(self, webdata: WebData):
        if webdata.soup.find(class_="error_string"):
            raise ValueError("No results found")
