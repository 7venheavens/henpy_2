from __future__ import annotations
from party_downloader.metadata.scrapers.base_metadata_scraper import BaseMetadataScraper
from pathlib import Path
from party_downloader.models.web_data import WebData
from party_downloader.helpers import Regexes


class JAVLibraryScraper(BaseMetadataScraper):
    COMPONENT_REGEX = Regexes.JAV
    SEARCH_TEMPLATE = "https://www.javlibrary.com/en/vl_searchbyid.php?keyword={}"

    def get_id_components(self, file: str | Path) -> tuple[str, str] | None:
        file = Path(file)
        groups = self.COMPONENT_REGEX.findall(file.stem)
        print(groups)
        if len(groups) != 1:
            raise Exception(f"Unable to extract ids: {file.stem}")

        id = f"{groups[0][0].upper()}-{groups[0][1]}"
        part = None
        if len(groups[0]) >= 3 and groups[0][2]:
            part = int(groups[0][2])

        res = {"id": id, "part": part, "name": id}
        return res

    @staticmethod
    def is_valid(webdata: WebData):
        if JAVLibraryScraper.is_multiple(webdata):
            raise ValueError("Multiple results found")
        if webdata.soup.find(text="Search returned no result."):
            raise ValueError("Invalid data")

    @staticmethod
    def is_multiple(webdata: WebData):
        videos = webdata.soup.find_all(class_="video")
        return len(videos) > 1
