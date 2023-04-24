from __future__ import annotations
from party_downloader.metadata.dumpers.base_metadata_dumper import BaseMetadataDumper
from party_downloader.metadata.scrapers.base_metadata_scraper import BaseMetadataScraper
from party_downloader.models.web_data import WebData
from pathlib import Path
from party_downloader.helpers import Regexes
import requests


class MSINScraper(BaseMetadataScraper):
    COMPONENT_REGEX = Regexes.FC2
    SEARCH_TEMPLATE = "https://db.msin.jp/branch/search?sort=movie&str={}"

    def __init__(self):
        super().__init__()
        self.session.cookies.set("age", "off")

    @classmethod
    def get_id_components(cls, file: str | Path) -> tuple[str, str] | None:
        res = super().get_id_components(file)
        if res:
            res["name"] = f'fc2-ppv-{res["id"]}'
        return res

    @staticmethod
    def is_multiple(webdata: WebData):
        if webdata.soup.find(class_="movie_view"):
            return True
        return False

    @staticmethod
    def is_valid(webdata: WebData):
        error = webdata.soup.find(class_="error_string")
        if error and error.text == "No Results":
            raise ValueError("No results found")

        if MSINScraper.is_multiple(webdata):
            raise ValueError("Multiple results found")
        MSINScraper.is_age_verified(webdata)

    @staticmethod
    def is_age_verified(webdata: WebData):
        target = webdata.soup.find(class_="error_massage")
        if target and target.text == "年齢確認":
            raise ValueError("Age verification required")
