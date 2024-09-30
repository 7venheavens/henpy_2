from __future__ import annotations


from abc import ABC
from pathlib import Path

from party_downloader.errors import MultipleResultsError
from party_downloader.models.web_data import WebData

from typing import Literal, Pattern

import requests

# from seleniumwire.webdriver import ChromeService
from selenium.webdriver.chrome.service import Service as ChromeService
import urllib3
from selenium.webdriver.remote.remote_connection import LOGGER
import logging

LOGGER.setLevel(logging.WARNING)

# from selenium.webdriver.chrome.service import Service as ChromeService


class BaseMetadataScraper(ABC):
    """Basemetadatascraper is used to obtain data for the various scrapers.
    Given a filename, it obtains the webdata for metadata extraction"""

    # the mandatory regex should have a ? component for the part number
    COMPONENT_REGEX: None | Pattern = None
    SEARCH_TEMPLATE: str = "https://example.com/search?q={}"
    OUTPUT_FORMAT: str = "{id} - [{studio}] - {title}"

    def __init__(self, session: requests.Session):
        self.session = session

    def get_id_components(self, file: str | Path) -> tuple[str, str] | None:
        """Gets the video id components from a given filename"""
        file = Path(file)
        groups = self.COMPONENT_REGEX.search(file.stem).groups()
        if len(groups) == 1:
            groups += (None,)

        res = {"id": groups[0], "part": groups[1], "name": groups[0]}
        if res["part"]:
            res["part"] = int(res["part"])
        return res

    def get_query_string(self, file: str | Path) -> str:
        """Builds the query string from the filename, raises an error if a filename cannot be found"""
        components = self.get_id_components(file)
        return components["id"]

    @staticmethod
    def is_multiple(webdata: WebData):
        """Checks if the metadata page matches to mult
        iple videos"""
        if False:
            raise ValueError("Invalid data")

    @staticmethod
    def is_valid(webdata: WebData):
        """Checks if the metadata page is valid and does not point to a "did not find" page"""
        if False:
            raise ValueError("Invalid data")

    def get_single_from_multiple(self, data) -> str:
        """Gets the single video from a multiple video page"""
        pass

    @classmethod
    def verify_age(cls, webdata):
        """Verifies the age of the user"""
        pass

    def search(self, query: str) -> WebData:
        req = self.session.get(self.SEARCH_TEMPLATE.format(query))
        res = WebData(req.url, req.text, session=self.session)
        # check if is valid
        try:
            self.is_valid(res)
        except MultipleResultsError:
            url = self.get_single_from_multiple(res)
            res = WebData(url, session=self.session)

        return res

    # overall method
    def process(
        self,
        file: str | Path,
        force: bool = False,
    ):
        """Processes a file, dumping it into an output directory

        Args:
            file_path (str|Path): The path to the file
            outdir (str|Path, optional): The output directory. Defaults to None.
        """
        # TODO: Check for cached file
        query_string = self.get_query_string(file)
        webdata = self.search(query_string)
        self.is_valid(webdata)
        return webdata
