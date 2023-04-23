import os
from pathlib import Path
import requests
from party_downloader.models.download_metadatum import DownloadMetadatum
from party_downloader.models.party_page import PartyCreatorPage, PartyPostPage

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
        """
        A blacklist consists of the following tuples:
        (source, creator, post): The post has already been downloaded
        """
        blacklist = set()
        for source in self.outdir.iterdir():
            for creator in source.iterdir():
                for post in creator.iterdir():
                    key = tuple(post.relative_to(self.outdir).as_posix().split("/"))
                    blacklist.add(key)
        return blacklist

    def _download_post(self, post: PartyPostPage):
        """Downloads all data for a given post. Assumes that a post is complete if not found"""
        outdir = self.outdir / post.dir_prefix
        os.makedirs(outdir, exist_ok=True)
        for datum in post.get_download_metadata():
            logger.info(f"Downloading {datum.filename}")
            if self.execute:
                self._download_file(outdir, datum)
        # write the page data after
        page_data_path = outdir / Path("content")
        with open(page_data_path, "w", encoding="utf-8") as f:
            f.write(post.page_data)

    def _download_file(self, outdir, datum: DownloadMetadatum):
        """
        Downloads the desired data to disk
        """
        resp = requests.get(datum.path)
        outpath = outdir / Path(datum.filename)
        with open(outpath, "wb") as f:
            f.write(resp.content)
        print(f"Written to {outpath}, {outdir}, {datum.filename}")

    def download_creator(self, creator_url):
        """
        Args:
            creator_url (TYPE): Description
            update_only (TYPE): Only gets more recent values. Terminates upon reaching a blacklisted item. Otherwise iterates through all pages
        """
        page = PartyCreatorPage.from_url(creator_url)
        logger.info(f"Processing Creator {page.creator_id}")
        # iterate over the pages in reverse order
        for page in page.pages:
            # Check if the first post is already downloaded (page fully downloaded)
            posts = list(page.child_posts)
            if posts[0].key in self.blacklist:
                logger.info(f"Skippin page {page.parsed_url}")
                continue
            logger.info(f"Processing page {page.parsed_url}")
            for post in posts[::-1]:
                if post.key in self.blacklist:
                    continue
                self._download_post(post)

    def download_post(self, post_url):
        post = PartyPostPage.from_url(post_url)
        self._download_post(post)
