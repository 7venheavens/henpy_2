from __future__ import annotations
from party_downloader.metadata.scrapers.base_metadata_scraper import BaseMetadataScraper
from pathlib import Path
from party_downloader.models.web_data import WebData
from party_downloader.helpers import Regexes


# This should probably pull from some more generic family of scrapers
class JavDBScraper(BaseMetadataScraper):
    COMPONENT_REGEX = Regexes.JAV
    SEARCH_TEMPLATE = "https://javdb.com/search?q={id}&locale=en"

    def __init__(self):
        super().__init__()
        self.session.cookies.set("locale", "en")

    def get_id_components(self, file: str | Path) -> tuple[str, str] | None:
        file = Path(file)
        groups = self.COMPONENT_REGEX.findall(file.stem)
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
        videos = webdata.soup.find("movie-list").find_all(class_="item")
        return len(videos) > 1

    @staticmethod
    def is_valid(webdata: WebData):
        # if webdata.soup.find(class_="alert-danger") or webdata.soup.find(
        #     text="No Result Found!"
        # ):
        if webdata.soup.find(text="No content yet"):
            raise ValueError("Invalid data")

    def search(self, query: str) -> WebData:
        print(f"Searching for {self.SEARCH_TEMPLATE.format(id=query)}")
        root = WebData(self.SEARCH_TEMPLATE.format(id=query))
        self.is_valid(root)
        # This one is always multiple
        matches = []
        video_tiles = root.soup.find(class_="movie-list").find_all(class_="item")
        for tile in video_tiles:
            tile_id = tile.find(class_="video-title").find("strong").text
            if tile_id == query:
                link = tile.find("a", href=True).attrs["href"]
                res = WebData(root.clean_url_link(link) + "?locale=en")
                matches.append(res)
        if len(matches) != 1:
            raise ValueError("Multiple matches found")
        print(f"Found {matches[0].url}")
        return matches[0]
