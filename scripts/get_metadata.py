from party_downloader.metadata.aggregate import aggregate_files
from party_downloader.metadata.dumpers.dumper import Dumper
from party_downloader.metadata.extractors import (
    FC2Extractor,
    MSINExtractor,
)
from party_downloader.metadata.scrapers import (
    FC2Scraper,
    MSINScraper,
    BaseMetadataScraper,
)
from pathlib import Path
import json
from party_downloader.models.web_data import WebData

choices = ["fc2", "msin"]


scrapers: dict[str, BaseMetadataScraper] = {
    "fc2": FC2Scraper(),
    "msin": MSINScraper(),
}

extractors = {
    "fc2": FC2Extractor,
    "msin": MSINExtractor,
}


def reprocess(target_dir, target_type, download_thumbnails):
    """Uses the existing run.json file to reprocess the files in the target directory

    Args:
        target_dir (_type_): _description_
        target_type (_type_): _description_
        download_thumbnails (_type_): _description_
    """
    pass


def main(target_dir, target_type, download_thumbnails, sleep):
    scraper = scrapers.get(target_type)
    if not scraper:
        raise ValueError("Provide a valid target type")

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
            Dumper.process(
                file_path=path,
                outdir=target_dir,
                extractor=extractor,
                part=part,
                dump_thumbnails=download_thumbnails,
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
    args = parser.parse_args()
    main(args.target_dir, args.target_type, args.download_thumbnails, args.sleep)
