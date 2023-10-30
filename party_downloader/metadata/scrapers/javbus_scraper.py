from __future__ import annotations
from party_downloader.metadata.scrapers.base_metadata_scraper import BaseMetadataScraper
from pathlib import Path
from party_downloader.models.web_data import WebData
from party_downloader.helpers import Regexes


# This should probably pull from some more generic family of scrapers
class JavBusScraper(BaseMetadataScraper):
    COMPONENT_REGEX = Regexes.JAV
    SEARCH_TEMPLATE = "https://www.javbus.com/en/search/{id}&type=&parent=ce"

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
    def is_multiple(webdata: WebData):
        videos = webdata.soup.find_all(class_="masonry-brick")
        return len(videos) > 1

    @staticmethod
    def is_valid(webdata: WebData):
        # if webdata.soup.find(class_="alert-danger") or webdata.soup.find(
        #     text="No Result Found!"
        # ):
        if webdata.soup.find(text="No Result Found!"):
            raise ValueError("Invalid data")
        if JavBusScraper.is_multiple(webdata):
            raise ValueError("Multiple results found")

    def search(self, query: str) -> WebData:
        res = WebData(self.SEARCH_TEMPLATE.format(id=query))
        self.is_valid(res)

        # if it's a single, we need to actually go to the page itself so we can unpack it
        video = res.soup.find("a", class_="movie-box", href=True)
        link = video.attrs["href"]
        # TODO: add a check to identify probable mismatches
        res = WebData(link)

        return res
