from party_downloader.metadata.dumpers.base_metadata_dumper import BaseMetadataDumper
from party_downloader.metadata.extractors.fc2_extractor import FC2Extractor
from party_downloader.models.web_data import WebData
from pathlib import Path
import re

FC2_REGEX = re.compile(r"fc2-ppv-(\d+)", re.IGNORECASE)


class FC2Dumper(BaseMetadataDumper):
    EXTRACTOR = FC2Extractor
    SEARCH_TEMPLATE = None
    GET_TEMPLATE = "https://adult.contents.fc2.com/article/{id_num}/"

    def get_query_string(self, file_name: str) -> str:
        return FC2_REGEX.search(file_name).group(1)

    def is_valid(self, webdata: WebData):
        if webdata.soup.find(class_="items_notfound_wp"):
            raise ValueError("Invalid data")

    def search(self, query: str) -> WebData:
        res = WebData(self.GET_TEMPLATE.format(id_num=query))
        self.is_valid(res)
        return res
