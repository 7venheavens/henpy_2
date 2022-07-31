from bs4 import BeautifulSoup
import os
from pathlib import Path
from dataclasses import dataclass
import re
import requests
from urllib.parse import urlparse, urljoin
from functools import cached_property
from copy import copy
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

    def download_post(self, post: PartyPostPage):
        """Downloads all data for a given post. Assumes that a post is complete if not found"""
        for datum in post.get_download_metadata():
            logger.info(f"Downloading {datum.filename}")
            outdir = self.outdir / Path(datum.target_dir)
            os.makedirs(outdir, exist_ok=True)
            outpath = outdir / Path(datum.filename)
            if self.execute:
                resp = requests.get(datum.path)
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
        # iteratet over the pages in reverse order
        for page in page.pages:
            # Check if the first post is already downloaded (page fully downloaded)
            posts = list(page.child_posts)
            if posts[0].key in self.blacklist:
                continue
            logger.info(f"Processing page {page.parsed_url}")
            for post in posts[::-1]:
                if post.key in blacklist:
                    continue
                self.download_post(post)

    def download_file(self, download_metadata):
        """
        Downloads the desired data to disk
        """
        pass
