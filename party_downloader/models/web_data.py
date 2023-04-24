from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests


class WebData:
    """Basic Class to store information from a scraped webpage"""

    URL_KEY_REGEX = None

    def __init__(self, url, page_data=None):
        self._page_data = None
        self._soup = None
        self.url = url
        self.parsed_url = urlparse(url)
        if page_data:
            self._page_data = page_data

    def __repr__(self):
        return f"<WebData: {self.parsed_url.geturl()}>"

    @property
    def soup(self):
        # lazily gets the soup when required
        if not self._soup:
            self._soup = BeautifulSoup(self.page_data, features="html.parser")
        return self._soup

    @property
    def page_data(self):
        # lazily gets the page data when required
        if not self._page_data:
            resp = requests.get(self.parsed_url.geturl())
            self._page_data = resp.text

        return self._page_data

    @classmethod
    def from_dump(cls, path, url):
        """Convenience method to load from a path to a file, instead of a file"""
        with open(path, encoding="utf-8") as f:
            page_data = f.read()
        result = cls(url)
        result._page_data = page_data
        return result

    @classmethod
    def from_url(cls, url):
        return cls(url)

    @classmethod
    def get_key(cls, path):
        return cls.URL_KEY_REGEX.search(path).groups()

    @property
    def key(self):
        return self.get_key(self.parsed_url.path)

    @property
    def root_url(self):
        return f"{self.parsed_url.scheme}://{self.parsed_url.netloc}"

    def get_url_query_params(self, url):
        parsed = urlparse(url)
        if not parsed.query:
            return {}
        res = {
            key: val for key, val in (arg.split("=") for arg in parsed.query.split("&"))
        }
        return res

    def clean_url_link(self, link):
        """Cleans a link to be a full URL"""
        if link.startswith("//"):
            return "https:" + link

        if link.startswith("/"):
            return f"{self.root_url}{link}"
        return link
