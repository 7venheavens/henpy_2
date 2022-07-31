from bs4 import BeautifulSoup
import os
from pathlib import Path
from dataclasses import dataclass
import re
import requests
from urllib.parse import urlparse, urljoin
from functools import cached_property
from copy import copy

import logging

logger = logging.getLogger("core")


class Downloader:
    def __init__(self, outdir, execute=False):
        self.outdir = Path(outdir)
        self.initialize_outdir()
        self.blacklist = self.generate_blacklist()
        self.execute = execute

    def initialize_outdir(self):
        os.makedirs(self.outdir, exist_ok=True)

    def generate_blacklist(self):
        blacklist = set()
        for source in self.outdir.iterdir():
            for creator in source.iterdir():
                for post in source.iterdir():
                    print(self.outdir, source, post.relative_to(self.outdir), post)
                    key = tuple(post.relative_to(self.outdir).as_posix().split("/"))
                    blacklist.add(key)
        print(blacklist)
        return blacklist

    def download_creator(self, creator_url, update_only=False):
        """
        Args:
            creator_url (TYPE): Description
            update_only (TYPE): Only gets more recent values. Terminates upon reaching a blacklisted item. Otherwise iterates through all pages
        """
        page = PartyCreatorPage.from_url(creator_url)
        logger.info(f"Processing Creator {page.creator_id}")
        # iteratet over the pages in reverse order
        for page in page.pages:
            if page.key in self.blacklist:
                if update_only:
                    return
                logger.info(f"Skipped page {page.parsed_url}")
                continue
            logger.info(f"Processing page {page.parsed_url}")
            for datum in page.get_download_metadata(blacklist=self.blacklist):
                logger.info(f"Downloading {datum.filename}")
                outdir = self.outdir / Path(datum.target_dir)
                os.makedirs(outdir, exist_ok=True)
                outpath = outdir / Path(datum.filename)
                if self.execute:
                    resp = requests.get(datum.path)
                    with open(outpath, "wb") as f:
                        f.write(resp.content)
                    print(f"Written to {outpath}, {outdir}, {datum.filename}")

    def download_file(self, download_metadata):
        """
        Downloads the desired data to disk
        """
        pass


@dataclass
class DownloadMetadatum:
    path: str
    target_dir: str
    filetype: str
    key: tuple
    filename: str = None

    def __post_init__(self):
        parsed = urlparse(self.path)
        _, fn = parsed.query.split("=")
        self.filename = fn


class PartyWebData:
    def __init__(self, url, page_data=None):
        self._page_data = None
        self._soup = None
        self.parsed_url = urlparse(url)
        if page_data:
            self._page_data = page_data

    def __repr__(self):
        return f"<PartyWebData: {self.parsed_url.geturl()}>"

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
            self._page_data = resp.txt

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
        return cls.url_regex.search(path).groups()

    @property
    def key(self):
        return self.get_key(self.parsed_url.path)

    @property
    def creator_id(self):
        return self.key[1]

    @property
    def root_url(self):
        return f"{self.parsed_url.scheme}://{self.parsed_url.netloc}"

    def get_url_query_params(self, url):
        parsed = urlparse(url)
        if not parsed.query:
            return {}
        res = {key: val for key, val in (arg.split("=") for arg in parsed.query.split("&"))}
        return res


class PartyCreatorPage(PartyWebData):
    url_regex = re.compile(r"""\/(\w+)\/user\/(\d+)""")

    @property
    def next_page_url(self):
        pages = self.soup.find_all("menu")[0]
        next_page = pages.find("a", {"title": "Next page"})
        next_url = (urljoin(self.root_url, next_page["href"]),)
        return next_url

    @property
    def next_page(self):
        if not self._next_page:
            return None
        return PartyCreatorPage.from_url(self.next_page_url)

    @cached_property
    def last_page_url(self):
        pages = self.soup.find_all("menu")[0]
        urls = pages.find_all("a")
        if not urls:
            return None

        # last element is usually the next page arrow
        last_page_url = urls[-1]
        if last_page_url["title"] == "Next page":
            last_page_url = urls[-2]
        return last_page_url["href"]

    @property
    def pages(self):
        # returns an iterator with pages in reverse order
        # get the latest link, then use that to derive all the other links. This uses a fixed 25 per page
        # TODO: CHECK IF THIS IS CONSTANT
        cur = self
        if not self.last_page_url:
            yield self
            return

        parse_result = urlparse(self.last_page_url)
        # BAD. MOVE THIS OUT
        last_page_offset = int(self.get_url_query_params(self.last_page_url)["o"])
        for offset in range(last_page_offset, -1, -25):
            yield PartyCreatorPage(parse_result._replace(netloc=self.parsed_url.netloc, query=f"o={offset}").geturl())

    def _get_cards(self):
        return self.soup.find_all("article", {"class": "post-card"})

    def get_child_posts(self, blacklist=None):
        if not blacklist:
            blacklist = set()

        for card_soup in self._get_cards():
            post_href = card_soup.find("a")["href"]
            if PartyPostPage.get_key(post_href) in blacklist:
                continue
            post_url = urljoin(self.root_url, post_href)
            post = PartyPostPage.from_url(post_url)
            yield post

    def get_download_metadata(self, blacklist=None):
        """Download metadata is an iterable of DownloadMetadatum objects"""
        if not blacklist:
            blacklist = set()

        for post_page in self.get_child_posts(blacklist=blacklist):
            if post_page.key in blacklist:
                continue
            for metadatum in post_page.get_download_metadata(blacklist=blacklist):
                yield metadatum

    def get_archive_metadata(self):
        pass


class PartyPostPage(PartyWebData):
    # e.g. .party/fantia/user/1470/post/925022
    url_regex = re.compile(r"""\/(\w+)\/user\/(\d+)\/post\/(\d+)""")

    @property
    def dir_prefix(self):
        return Path("/".join(self.key))

    def get_download_metadata(self, blacklist=None):
        """Download metadata is an iterable of DownloadMetadatum objects"""
        if not blacklist:
            blacklist = set()

        attachment_soup = self.soup.find_all("a", {"class": "post__attachment-link"})
        image_soup = self.soup.find_all("a", {"class": "fileThumb"})
        for esoup in attachment_soup:
            md = DownloadMetadatum(
                urljoin(self.root_url, esoup["href"]),
                self.dir_prefix,
                key=self.key + (esoup["href"],),
                filetype="attachment",
            )
            yield md
        for isoup in image_soup:
            md = DownloadMetadatum(
                urljoin(self.root_url, isoup["href"]),
                self.dir_prefix,
                key=self.key + (isoup["href"],),
                filetype="image",
            )
            yield md

        # yield DownloadMetadatum(isoup["href"], self.dir_prefix, key=self.key + (isoup["href"],), filetype="image")

    def get_(self):
        pass
