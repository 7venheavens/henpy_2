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
    FOLDER_OUTPUT_FORMAT: str = "{id} - [{studio}] - {title}"
    FILE_OUTPUT_FORMAT: str = "{id}"

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
        if not dump_thumbnails:
            return
        print("Dumping thumbnails")
        thumb_dir = outdir / "thumbs"
        for i, thumb_url in enumerate(extractor.thumbnail_urls):
            thumb_path = thumb_dir / f"{i}.jpg"
            with open(thumb_path, "wb") as f:
                f.write(requests.get(thumb_url).content)

    @classmethod
    def _dump_run_data(cls, extractor: BaseMetadataExtractor, outdir):
        html_name = f"{outdir.stem}.html"
        with open(outdir / html_name, "w", encoding="utf-8") as f:
            f.write(extractor.webdata.page_data)
        run_data = {
            "dump_name": html_name,
            "url": extractor.webdata.url,
        }
        with open(outdir / "run.json", "w", encoding="utf-8") as f:
            json.dump(run_data, f)

    @staticmethod
    def _prepare_outdir(outdir: Path):
        outdir.mkdir(exist_ok=True)
        (outdir / "thumbs").mkdir(exist_ok=True)

    @classmethod
    def process(
        cls,
        file_path: str | Path,
        extractor,
        outdir: str | Path,
        part: int | None = None,
        dump_thumbnails: bool = True,
        rename_files: bool = True,
        execute=True,
    ):
        """Processes a file, dumping it into an output directory

        Args:
            file_path (str|Path): The path to the file
            outdir (str|Path, optional): The output directory. Defaults to None.
        """
        file_path: Path = Path(file_path)

        # Maybe generate the outdir from the name
        # name = cls.FOLDER_OUTPUT_FORMAT.format(**extractor.metadata)
        # Can be long, need some checks for this
        outdir = Path(outdir) / extractor.id

        cls._prepare_outdir(outdir)

        cls._dump_media(extractor, outdir, dump_thumbnails=dump_thumbnails)

        cls._dump_run_data(extractor, outdir)

        base_name = cls.FILE_OUTPUT_FORMAT.format(**extractor.metadata)
        with open(outdir / f"{base_name}.nfo", "w", encoding="utf-8") as f:
            f.write(extractor.metadata_nfo)
        if part:
            new_file_name = f"{base_name} - pt{part}{file_path.suffix}"
        else:
            new_file_name = f"{base_name}{file_path.suffix}"

        print("NEW NAME", new_file_name)

        if not execute:
            return
        shutil.move(file_path, outdir / new_file_name)
