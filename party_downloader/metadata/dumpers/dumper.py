from __future__ import annotations
from party_downloader.metadata.extractors import BaseMetadataExtractor
from abc import ABC, abstractmethod
from pathlib import Path
import os
from party_downloader.models.web_data import WebData
import shutil
import json

import requests


class Dumper:
    OUTPUT_FORMAT: str = "{id} - [{studio}] - {title}"

    # Application of the extractor
    @classmethod
    def _dump_media(
        cls,
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

    @classmethod
    def process(
        cls,
        file_path: str | Path,
        extractor,
        outdir: str | Path | None = None,
        part: int | None = None,
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
        else:
            outdir = Path(outdir)
            outdir.makedirs(exist_ok=True)

        cls._dump_media(extractor, outdir, dump_thumbnails=dump_thumbnails)
        with open(f"{extractor.id}.nfo", "w") as f:
            f.write(extractor.metadata_nfo)

        new_name = cls.OUTPUT_FORMAT.format(**extractor.__dict__)
        if part:
            new_name += f" - pt{part}"
        if rename_files:
            shutil.move(file_path, outdir / new_name)
