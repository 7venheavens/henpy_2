from __future__ import annotations
from party_downloader.metadata.scrapers.base_metadata_scraper import BaseMetadataScraper
from pathlib import Path
from party_downloader.models.web_data import WebData
from party_downloader.helpers import Regexes


# This should probably pull from some more generic family of scrapers
class AVBaseScraper(BaseMetadataScraper):
    COMPONENT_REGEX = Regexes.JAV
    SEARCH_TEMPLATE = "https://www.avbase.net/works?q={id}"

    def get_id_components(
        self, file: str | Path, strip_hyphens=True
    ) -> tuple[str, str] | None:
        file = Path(file)
        groups = self.COMPONENT_REGEX.findall(file.stem)
        print(groups)
        if len(groups) != 1:
            raise Exception(f"Unable to extract ids: {file.stem}")

        if strip_hyphens:
            id = f"{groups[0][0].upper()}{groups[0][1]}"
        else:
            id = f"{groups[0][0].upper()}-{groups[0][1]}"
        part = None
        if len(groups[0]) >= 3 and groups[0][2]:
            part = int(groups[0][2])

        res = {"id": id, "part": part, "name": id}
        return res

    @staticmethod
    def is_multiple(webdata: WebData):
        core = webdata.soup.find(class_="grid sm:grid-cols-2 gap-4")
        targets = list(core.children)
        return len(targets) > 1

    @staticmethod
    def is_valid(webdata: WebData):
        # if webdata.soup.find(class_="alert-danger") or webdata.soup.find(
        #     text="No Result Found!"
        # ):
        if webdata.soup.find(text="No Result Found!"):
            raise ValueError("Invalid data")
        if AVBaseScraper.is_multiple(webdata):
            raise ValueError("Multiple results found")

    @staticmethod
    def get_target_from_single_result(webdata: WebData):
        target = webdata.soup.find(class_="grid sm:grid-cols-2 gap-4").find("div")
        link = target.find_all("div", recursive=False)[1].find_all("a", href=True)[-1]

        return link.attrs["href"]

    def search(self, query: str) -> WebData:
        res = WebData(self.SEARCH_TEMPLATE.format(id=query))
        self.is_valid(res)

        # if it's a single, we need to actually go to the page itself so we can unpack it
        link = self.get_target_from_single_result(res)
        # TODO: add a check to identify probable mismatches
        res = WebData(link)

        return res
