from __future__ import annotations
from party_downloader.metadata.aggregate import aggregate_files
from party_downloader.metadata.dumpers.dumper import Dumper
from party_downloader.metadata.extractors import (
    FC2Extractor,
    MSINExtractor,
    JavLibraryExtractor,
    JavBusExtractor,
    JavDBExtractor,
    AVBaseExtractor,
)
from party_downloader.metadata.scrapers import (
    FC2Scraper,
    MSINScraper,
    BaseMetadataScraper,
    JAVLibraryScraper,
    JavBusScraper,
    JavDBScraper,
    AVBaseScraper,
)
from pathlib import Path
import json
from party_downloader.models.web_data import WebData
from party_downloader.helpers import make_folder_from_fanart, Regexes
import logging


choices = ["fc2", "msin", "javlibrary", "javbus", "javdb", "avbase"]


scrapers: dict[str, BaseMetadataScraper] = {
    "fc2": FC2Scraper,
    "msin": MSINScraper,
    "javlibrary": JAVLibraryScraper,
    "javbus": JavBusScraper,
    "javdb": JavDBScraper,
    "avbase": AVBaseScraper,
}

extractors = {
    "fc2": FC2Extractor,
    "msin": MSINExtractor,
    "javlibrary": JavLibraryExtractor,
    "javbus": JavBusExtractor,
    "javdb": JavDBExtractor,
    "avbase": AVBaseExtractor,
}

regexes = {
    "fc2": Regexes.FC2,
    "jav": Regexes.JAV,
    "avbase": Regexes.JAV_NOHYPHEN,
    "jav_prefix": Regexes.JAV_PREFIX,
    "carib": Regexes.CARIB,
}


def reprocess_dir(
    target_dir: Path | str,
    extractor,
    scraper,
    download_thumbnails=True,
    dry_run=True,
    override_regex=None,
):
    """Uses the existing run.json file and associated html files to reprocess the files in the target directory

    Args:
        target_dir _
        extractor (_type_): _description_
        download_thumbnails (_type_): _description_
    """
    target_dir = Path(target_dir)
    if override_regex:
        scraper.COMPONENT_REGEX = override_regex

    if not (target_dir / "run.json").exists():
        raise ValueError("No run.json file found in target directory")
    with open(target_dir / "run.json", "r") as f:
        run_data = json.load(f)
    webdata = WebData.from_dump(target_dir / run_data["dump_name"], run_data["url"])
    extractor = extractor(webdata)

    holder, unprocessed = aggregate_files(target_dir, scraper)
    assert len(holder) == 1

    for name, file_data in holder.items():
        print(f"reprocessing video: {name}")
        for path, part in file_data:
            dump_dir = Dumper.process(
                file_path=path,
                outdir=target_dir,
                extractor=extractor,
                part=part,
                dump_thumbnails=download_thumbnails,
            )
            if not dump_dir or not (dump_dir / "fanart.jpg").exists():
                continue
            make_folder_from_fanart(
                (dump_dir / "fanart.jpg"), (dump_dir / "folder.jpg")
            )


def main(
    target_dir,
    target_type,
    download_thumbnails,
    sleep,
    dry_run=False,
    override_regex=None,
    cookies: list[dict] = {},
    headers: dict = {},
    engine="requests",
    webdriver_path=None,
    binary_path=None,
    fail_fast=False,
):
    scraper = scrapers.get(target_type)(
        engine=engine,
        driver_path=webdriver_path,
        binary_path=binary_path,
        cookies=cookies,
    )
    if not scraper:
        raise ValueError("Provide a valid target type")

    if override_regex:
        scraper.COMPONENT_REGEX = override_regex

    if headers:
        scraper.session.headers.update(headers)

    target_dir = Path(target_dir)

    holder, unprocessed = aggregate_files(target_dir, scraper)
    print(f"Beginning processing of {len(holder)} videos")
    for name, file_data in holder.items():
        print(f"Processing video: {name}")
        # Check if existing data exists, and use the previous load
        # if (outdir / "run.json").exists():
        #     with open(outdir / "run.json", "r") as f:
        #         run_data = json.load(f)
        #     webdata = WebData.from_dump(outdir / run_data["dump_name"], run_data["url"])
        try:
            webdata = scraper.process(file_data[0][0])
        except ValueError as e:
            print(f"Could not process video: {name}, {e}")
            if fail_fast:
                raise e
            continue
        extractor = extractors[args.target_type](webdata)
        for path, part in file_data:
            print(f"Processing file: {path}, part: {part}")
            if dry_run:
                continue
            dump_dir = Dumper.process(
                file_path=path,
                outdir=target_dir,
                extractor=extractor,
                part=part,
                dump_thumbnails=download_thumbnails,
            )

            if target_type == "javlibrary":
                if not dry_run and dump_dir and (dump_dir / "fanart.jpg").exists():
                    make_folder_from_fanart(
                        (dump_dir / "fanart.jpg"), (dump_dir / "folder.jpg")
                    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("target_dir", help="Directory containing files to process")
    parser.add_argument(
        "target_type",
        help="Type of target to process",
        choices=choices,
    )
    parser.add_argument(
        "--download_thumbnails", action="store_true", help="Download thumbnails"
    )
    parser.add_argument(
        "--sleep", help="Sleep time between requests", type=int, default=2
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Dry run, don't actually download anything",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--override-regex",
        help="Override the regex used to match",
        choices=regexes.keys(),
        default=None,
    )
    parser.add_argument(
        "--reprocess",
        action="store_true",
        help="Reprocess the target directory, using only existing data",
        default=False,
    )
    parser.add_argument(
        "--cookies",
        help="Cookies to pass to requests",
        default=None,
    )
    parser.add_argument(
        "--headers",
        help="Headers to pass to requests",
        default=None,
    )
    parser.add_argument(
        "--webdriver-path",
        help="Path to the webdriver for selenium",
        default=None,
    )
    parser.add_argument(
        "--engine",
        help="Engine to use for scraping",
        choices=["requests", "selenium"],
        default="requests",
    )
    parser.add_argument(
        "--binary-path",
        help="Path to the browser binary for selenium",
        default=None,
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Fail fast on errors",
    )
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.cookies and args.cookies.endswith(".json"):
        with open(args.cookies, "r") as f:
            cookies = json.load(f)

    else:
        cookies = json.loads(args.cookies) if args.cookies else {}

    if args.headers and args.headers.endswith(".json"):
        with open(args.headers, "r") as f:
            headers = json.load(f)

    else:
        headers = json.loads(args.headers) if args.headers else {}

    if args.reprocess:
        reprocess_dir(
            args.target_dir,
            extractors.get(args.target_type),
            scrapers.get(args.target_type),
            args.download_thumbnails,
            dry_run=args.dry_run,
            override_regex=regexes.get(args.override_regex),
        )

    else:
        main(
            args.target_dir,
            args.target_type,
            args.download_thumbnails,
            args.sleep,
            dry_run=args.dry_run,
            override_regex=regexes.get(args.override_regex),
            cookies=cookies,
            headers=headers,
            engine=args.engine,
            webdriver_path=args.webdriver_path,
            binary_path=args.binary_path,
            fail_fast=args.fail_fast,
        )
