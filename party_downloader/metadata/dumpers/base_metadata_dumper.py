from __future__ import annotations
from party_downloader.metadata.extractors import BaseMetadataExtractor
from abc import ABC, abstractmethod
from pathlib import Path
import os
from party_downloader.models.web_data import WebData
import shutil
import json

import requests


class BaseMetadataDumper(ABC):
    """MetadataDumper is the base class for all metadata dumpers
    After setting up the folder already, the metadataDumper will dump the metadata straight into the folder
    Metadata dumpers are utility classes used to query a website for metadata and extracting a WebData object from them

    The process method, when run on a file, will attempt to identify the ID key from the file, query the db website for it
    and then extract the metadata from the page
    """

    EXTRACTOR: BaseMetadataExtractor = BaseMetadataExtractor
    SEARCH_TEMPLATE: str = "https://example.com/search?q={}"
    GET_TEMPLATE: str = "https://example.com/get/{}"
    OUTPUT_FORMAT: str = "{id} - [{studio}] - {title}"

    # Search and idenfitication of the webdata for the extractor

    @abstractmethod
    def get_query_string(self, file_name: str) -> str:
        """Builds the query string from the filename, raises an error if a filename cannot be found"""
        return file_name

    def is_valid(self, webdata: WebData):
        """Checks if the metadata page is valid and does not point to a "did not find" page"""
        if False:
            raise ValueError("Invalid data")

    def search(self, query: str) -> WebData:
        req = requests.get(self.SEARCH_TEMPLATE.format(query))
        # check if is valid
        self.is_valid(req.text)
        return WebData(req.url)

    def prepare_extractor(self, file_path: Path) -> BaseMetadataExtractor:
        query_string = self.get_query_string(file_path.stem)
        # Check if we already have a cached webdata so we don't have to make a request
        # The cached html file will be stored in the same folder as the video
        # This is generally done for testing/debugging purposes
        # We'll export a run data json and a raw html dump
        if (file_path.parent / "run.json").exists():
            with open(file_path.parent / "run.json", "r") as f:
                run_data = json.load(f)
            web_data = WebData.from_dump(
                file_path.parent / run_data["dump_name"], run_data["url"]
            )
            extractor = self.EXTRACTOR(web_data)

        else:
            web_data = self.search(query_string)
            extractor = self.EXTRACTOR(web_data)
        return extractor

    # Application of the extractor
    def _dump_media(
        self,
        extractor: BaseMetadataExtractor,
        outdir: str,
        dump_thumbnails: bool = True,
    ):
        cover_url = extractor.cover_url
        if cover_url:
            cover_path = outdir / "folder.jpg"
            with open(cover_path, "wb") as f:
                f.write(requests.get(cover_url).content)

        # Dump the thumbnails
        thumb_dir = outdir / "thumbs"
        for i, thumb_url in enumerate(extractor.thumbnail_urls):
            thumb_path = thumb_dir / f"{i}.jpg"
            with open(thumb_path, "wb") as f:
                f.write(requests.get(thumb_url).content)

    # overall method
    def process(
        self,
        file_path: str | Path,
        outdir: str | Path | None = None,
        dump_thumbnails: bool = True,
        rename_files: bool = True,
    ):
        """Processes a file, dumping it into an output directory

        Args:
            file_path (str|Path): The path to the file
            outdir (str|Path, optional): The output directory. Defaults to None.
        """
        file_path: Path = Path(file_path)
        if not outdir:
            outdir = file_path.parent

        extractor = self.prepare_extractor(file_path)

        # Only if successful, do we make the outputs
        new_outdir = Path(outdir) / self.OUTPUT_FORMAT.format(**extractor.__dict__)
        os.makedirs(new_outdir, exist_ok=True)
        self._dump_media(extractor, new_outdir, dump_thumbnails=dump_thumbnails)
        with open(f"{extractor.id}.nfo", "w") as f:
            f.write(extractor.metadata_nfo)
        if rename_files:
            shutil.move(file_path, new_outdir / file_path.name)
