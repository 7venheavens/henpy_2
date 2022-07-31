import re
from urllib.parse import urlparse, urljoin
from party_downloader.models.party_web_data import PartyWebData
from party_downloader.models.download_metadatum import DownloadMetadatum
from functools import cached_property
from pathlib import Path


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
            yield PartyCreatorPage(
                parse_result._replace(
                    netloc=self.parsed_url.netloc, query=f"o={offset}"
                ).geturl()
            )

    def _get_cards(self):
        return self.soup.find_all("article", {"class": "post-card"})

    @property
    def child_posts(self):
        for card_soup in self._get_cards():
            post_href = card_soup.find("a")["href"]
            post_url = urljoin(self.root_url, post_href)
            post = PartyPostPage.from_url(post_url)
            yield post

    def get_download_metadata(self):
        """Download metadata is an iterable of DownloadMetadatum objects"""
        for post_page in self.get_child_posts():
            for metadatum in post_page.get_download_metadata():
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
                key=self.key + (esoup["href"],),
                filetype="attachment",
            )
            yield md
        for isoup in image_soup:
            md = DownloadMetadatum(
                urljoin(self.root_url, isoup["href"]),
                key=self.key + (isoup["href"],),
                filetype="image",
            )
            yield md
