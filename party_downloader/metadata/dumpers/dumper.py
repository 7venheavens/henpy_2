from __future__ import annotations
from party_downloader.metadata.extractors import BaseMetadataExtractor
from pathlib import Path

import shutil
import json
import re


class Dumper:
    FOLDER_OUTPUT_FORMAT: str = "{id} [{studio}] - {title}"
    FOLDER_OUTPUT_FORMAT_SHORT: str = "{id} - {title}"
    FOLDER_OUTPUT_FORMAT_SHORTEST: str = "{id}"
    FILE_OUTPUT_FORMAT: str = "{id}"

    def __init__(self, session) -> None:
        self.session = session

    # Application of the extractor
    def _dump_media(
        self,
        extractor: BaseMetadataExtractor,
        outdir: str,
        dump_thumbnails: bool = True,
    ):
        cover_url = extractor.cover_url
        cover_path = outdir / "folder.jpg"
        if cover_url and not cover_path.exists():
            try:
                print("Download flow")
                self.session.download_file(cover_url, cover_path)
            except AttributeError:
                print("Direct write flow")
                with open(cover_path, "wb") as f:
                    f.write(self.session.get(cover_url).content)

        background_url = extractor.background_url
        background_path = outdir / "fanart.jpg"
        if background_url:
            try:
                self.session.download_file(background_url, background_path)
            except AttributeError:
                if not background_path.exists():
                    with open(background_path, "wb") as f:
                        f.write(self.session.get(background_url).content)

        # Dump the thumbnails
        if not dump_thumbnails:
            return
        print("Dumping thumbnails")
        thumb_dir = outdir / "thumbs"
        for i, thumb_url in enumerate(extractor.thumbnail_urls):
            thumb_path = thumb_dir / f"{i}.jpg"
            if not thumb_path.exists():
                with open(thumb_path, "wb") as f:
                    f.write(self.session.get(thumb_url).content)

    def _dump_run_data(self, extractor: BaseMetadataExtractor, outdir):
        html_name = f"{outdir.stem}.html"
        with open(outdir / html_name, "w", encoding="utf-8") as f:
            f.write(extractor.webdata.page_data)
        run_data = {
            "dump_name": html_name,
            "url": extractor.webdata.url,
        }
        with open(outdir / "run.json", "w", encoding="utf-8") as f:
            json.dump(run_data, f)

    def _prepare_name(self, metadata):
        """Returns the output name for the metadata"""
        # Figure out which template to use intelligently, using the length of the title
        # This is because ZFS and some other file systems have a limit on the length of the file name (255 bytes)
        name = self.FOLDER_OUTPUT_FORMAT.format(**metadata)
        # Can be long, need some checks for this
        if len(name.encode("utf-8")) > 250:
            name = self.FOLDER_OUTPUT_FORMAT_SHORT.format(**metadata)
        if len(name.encode("utf-8")) > 250:
            name = self.FOLDER_OUTPUT_FORMAT_SHORTEST.format(**metadata)
        # Clean out illegal characters
        name = re.sub(r"[<>:\"/\\|?*]", "", name)
        name = name.replace("\u3000", " ")
        return name

    @staticmethod
    def _prepare_outdir(outdir: Path):
        outdir.mkdir(exist_ok=True)
        (outdir / "thumbs").mkdir(exist_ok=True)

    def process(
        self,
        file_path: str | Path,
        extractor,
        outdir: str | Path,
        part: int | None = None,
        dump_thumbnails: bool = True,
        rename_files: bool = True,
        execute=True,
    ) -> Path | None:
        """Processes a file, dumping it into an output directory. Returns the output directory

        Args:
            file_path (str|Path): The path to the file
            outdir (str|Path, optional): The output directory. Defaults to None.
        """
        # Maybe generate the outdir from the name
        data = extractor.metadata
        data["title"] = data["title"].replace(f" {extractor.id}", "")
        name = self._prepare_name(data)
        outdir = Path(outdir) / name
        try:
            self._prepare_outdir(outdir)
        except Exception as e:
            print(f"Could not prepare outdir: {outdir}. Exception: {e}")
            return

        self._dump_media(extractor, outdir, dump_thumbnails=dump_thumbnails)
        raise

        self._dump_run_data(extractor, outdir)

        base_name = self.FILE_OUTPUT_FORMAT.format(**extractor.metadata)
        with open(outdir / f"{base_name}.nfo", "w", encoding="utf-8") as f:
            f.write(extractor.metadata_nfo)
        if part:
            new_file_name = f"{base_name} - pt{part}{file_path.suffix}"
        else:
            new_file_name = f"{base_name}{file_path.suffix}"

        print("NEW NAME", new_file_name)

        if not execute:
            return outdir
        if (outdir / new_file_name).exists():
            raise Exception(f"File {new_file_name} already exists, skipping")
        shutil.move(file_path, outdir / new_file_name)
        return outdir
