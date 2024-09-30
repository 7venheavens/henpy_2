from seleniumbase import SB
import requests
import seleniumbase as sb
from seleniumwire import webdriver
from time import sleep
from pathlib import Path
from typing import Literal
import urllib3
import logging

logger = logging.getLogger(__name__)


class SeleniumSession:
    def __init__(
        self, driver_path, first_load_url=None, binary_path=None, cookies=None
    ):
        self.headers = {}
        options = webdriver.ChromeOptions()
        if binary_path:
            options.binary_location = binary_path
            data_path = Path(binary_path).parent / "User Data"
            options.add_argument(
                f"--user-data-dir={data_path}"
            )  # e.g. C:\Users\You\AppData\Local\Google\Chrome\User Data
            options.add_argument(f"--profile-directory=Default")

        self.driver = sb.Driver(uc=True)

    @property
    def cookies(self):
        class CookieJar:
            @classmethod
            def set(cls, name, value, **kwargs):
                print(name, value, kwargs)
                self.driver.add_cookie({"name": name, "value": value, **kwargs})

        print("Cookies:", self.driver.get_cookies())

        return CookieJar

    def interceptor(self, request):
        for key, value in self.headers.items():
            request.headers[key] = value

    def get(self, url):
        self.driver.get(url)

        if (
            "Enable JavaScript and cookies to continue" in self.driver.page_source
            or "Verifying that you are human" in self.driver.page_source
            or "Just a moment..." in self.driver.page_source
        ):
            print("Waiting for user input. Please resolve the captcha.")
            input("Press enter to continue")

        # mocks the requests response
        resp = requests.Response()
        resp.url = self.driver.current_url
        resp._content = self.driver.page_source.encode("utf-8")
        return resp

    def download_image(self, selector, folder, file_name):
        element = self.driver.find_element_by_css_selector(selector)
        src = element.get_attribute("src")
        urllib3.disable_warnings()
        with requests.get(src, stream=True, verify=False) as r:
            r.raise_for_status()
            with open(folder / file_name, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)


class SBSession:
    def __init__(self):
        self._sb = SB(uc=True)
        self.sb = self._sb.__enter__()
        self.first_get = True

    def get(self, url) -> requests.Response:
        logger.info("Getting url: %s", url)
        self.sb.open(url)
        if self.first_get:
            self.first_get = False
            sleep(3)
        else:
            sleep(0.5)

        self.sb.wait_for_ready_state_complete()
        source = self.sb.get_page_source()
        resp = requests.Response()
        resp.url = url
        resp._content = source.encode("utf-8")
        return resp

    def download_file(self, url, path: Path):
        print(f"Downloading {url} to {path.parent.absolute()}, {path.name}")
        self.sb.open(url)
        image = self.sb.find_element("img")
        image.screenshot(str(path))
        self.sb.assert_downloaded_file(path)


def setup_session(
    engine: Literal["requests", "selenium", "seleniumbase"] = "requests",
    driver_path=None,
    binary_path=None,
    cookies=None,
):
    if engine == "requests":
        session = requests.Session()
        if cookies:
            for cookie in cookies:
                session.cookies.set(**cookie)
    elif engine == "selenium":
        if not driver_path:
            raise ValueError("Driver path required for selenium")
        session = SeleniumSession(
            driver_path=driver_path,
            binary_path=binary_path,
            cookies=cookies,
        )
    elif engine == "seleniumbase":
        session = SBSession()

    return session
