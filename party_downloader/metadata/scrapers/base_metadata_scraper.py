from __future__ import annotations

from abc import ABC
from pathlib import Path
from time import sleep
from party_downloader.models.web_data import WebData

from typing import Literal, Pattern

import requests
from seleniumwire import webdriver

# from seleniumwire.webdriver import ChromeService
from selenium.webdriver.chrome.service import Service as ChromeService

# from selenium.webdriver.chrome.service import Service as ChromeService


class SeleniumSession:
    def __init__(self, driver_path):
        self.headers = {}

        self.driver = webdriver.Chrome(
            options=webdriver.ChromeOptions(),
            service=ChromeService(driver_path),
        )
        self.driver.request_interceptor = self.interceptor

    @property
    def cookies(self):
        class CookieJar:
            @classmethod
            def set(self, key, value, **kwargs):
                self.driver.add_cookie({"name": key, "value": value, **kwargs})

        return self._cookies

    def interceptor(self, request):
        for key, value in self.headers.items():
            request.headers[key] = value

    def get(self, url):
        self.driver.get(url)
        if "Enable JavaScript and cookies to continue" in self.driver.page_source:
            print("Waiting for user input. Please resolve the captcha.")
            input("Press enter to continue")

        print(self.driver.page_source)
        # mocks the requests response
        resp = requests.Response()
        resp.url = self.driver.current_url
        resp._content = self.driver.page_source.encode("utf-8")
        return resp


class BaseMetadataScraper(ABC):
    """Basemetadatascraper is used to obtain data for the various scrapers.
    Given a filename, it obtains the webdata for metadata extraction"""

    # the mandatory regex should have a ? component for the part number
    COMPONENT_REGEX: None | Pattern = None
    SEARCH_TEMPLATE: str = "https://example.com/search?q={}"
    OUTPUT_FORMAT: str = "{id} - [{studio}] - {title}"

    def __init__(
        self, engine: Literal["requests", "selenium"] = "requests", driver_path=None
    ):
        if engine == "requests":
            self.session = requests.Session()
        elif engine == "selenium":
            if not driver_path:
                raise ValueError("Driver path required for selenium")
            self.session = SeleniumSession(driver_path=driver_path)

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

    @classmethod
    def verify_age(cls, webdata):
        """Verifies the age of the user"""
        pass

    def search(self, query: str) -> WebData:
        req = self.session.get(self.SEARCH_TEMPLATE.format(query))
        res = WebData(req.url, req.text, session=self.session)
        # check if is valid
        self.is_valid(res)
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
