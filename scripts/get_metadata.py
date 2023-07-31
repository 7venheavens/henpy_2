from party_downloader.metadata.aggregate import aggregate_files
from party_downloader.metadata.dumpers.dumper import Dumper
from party_downloader.metadata.extractors import (
    FC2Extractor,
    MSINExtractor,
    JavLibraryExtractor,
    JavBusExtractor,
)
from party_downloader.metadata.scrapers import (
    FC2Scraper,
    MSINScraper,
    BaseMetadataScraper,
    JAVLibraryScraper,
    JavBusScraper,
)
from pathlib import Path
import json
from party_downloader.models.web_data import WebData
from party_downloader.helpers import make_folder_from_fanart, Regexes
import logging


choices = ["fc2", "msin", "javlibrary", "javbus"]


scrapers: dict[str, BaseMetadataScraper] = {
    "fc2": FC2Scraper(),
    "msin": MSINScraper(),
    "javlibrary": JAVLibraryScraper(),
    "javbus": JavBusScraper(),
}

extractors = {
    "fc2": FC2Extractor,
    "msin": MSINExtractor,
    "javlibrary": JavLibraryExtractor,
    "javbus": JavBusExtractor,
}

regexes = {
    "fc2": Regexes.FC2,
    "jav": Regexes.JAV,
    "jav_prefix": Regexes.JAV_PREFIX,
}


def reprocess(target_dir, target_type, download_thumbnails):
    """Uses the existing run.json file to reprocess the files in the target directory

    Args:
        target_dir (_type_): _description_
        target_type (_type_): _description_
        download_thumbnails (_type_): _description_
    """
    pass


def main(
    target_dir,
    target_type,
    download_thumbnails,
    sleep,
    dry_run=False,
    override_regex=None,
):
    scraper = scrapers.get(target_type)
    if not scraper:
        raise ValueError("Provide a valid target type")

    if override_regex:
        scraper.COMPONENT_REGEX = override_regex

    target_dir = Path(target_dir)

    holder, unprocessed = aggregate_files(target_dir, scraper)

    for name, file_data in holder.items():
        print(f"Processing video: {name}")
        # Check if existing data exists, and use the previous load
        # if (outdir / "run.json").exists():
        #     with open(outdir / "run.json", "r") as f:
        #         run_data = json.load(f)
        #     webdata = WebData.from_dump(outdir / run_data["dump_name"], run_data["url"])
        # else:
        try:
            webdata = scraper.process(file_data[0][0])
        except ValueError as e:
            print(f"Could not process video: {name}, {e}")
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
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    main(
        args.target_dir,
        args.target_type,
        args.download_thumbnails,
        args.sleep,
        dry_run=args.dry_run,
        override_regex=regexes.get(args.override_regex),
    )
