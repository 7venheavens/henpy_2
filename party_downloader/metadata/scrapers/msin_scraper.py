from __future__ import annotations
from party_downloader.metadata.dumpers.base_metadata_dumper import BaseMetadataDumper
from party_downloader.metadata.scrapers.base_metadata_scraper import BaseMetadataScraper
from party_downloader.models.web_data import WebData
from pathlib import Path
from party_downloader.helpers import Regexes
import requests
import re


class MSINScraper(BaseMetadataScraper):
    COMPONENT_REGEX = Regexes.FC2
    SEARCH_TEMPLATE = "https://db.msin.jp/branch/search?sort=movie&str={}"

    def __init__(self):
        super().__init__()
        self.session.cookies.set("age", "off")

    def get_id_components(self, file: str | Path) -> tuple[str, str] | None:
        res = super().get_id_components(file)
        if res:
            res["name"] = f'fc2-ppv-{res["id"]}'
        return res

    @staticmethod
    def is_multiple(webdata: WebData):
        res = re.findall(f"\w+\s+の検索結果\s+\d+件", webdata.page_data)
        return bool(res)

    @staticmethod
    def is_valid(webdata: WebData):
        error = webdata.soup.find(class_="error_string")
        if error and error.text == "No Results":
            raise ValueError("No results found")

        if MSINScraper.is_multiple(webdata):
            raise ValueError("Multiple results found")
        # check for 404
        if webdata.soup.find(class_="error_number", text="404"):
            raise ValueError("404 Not found")

        MSINScraper.is_age_verified(webdata)

    @staticmethod
    def is_age_verified(webdata: WebData):
        target = webdata.soup.find(class_="error_massage")
        if target and target.text == "年齢確認":
            raise ValueError("Age verification required")
