"""Scripts to handle bulk annotation of videos which might not have existing metadata
"""
import argparse
from party_downloader.metadata.extractors import BaseMetadataExtractor
import os
import shutil


class CustomMetadataExtractor(BaseMetadataExtractor):
    def __init__(self, **kwargs):
        super().__init__(None)
        self.data = kwargs
        for field in self.fields:
            if not getattr(self, field, None):
                continue

            setattr(self, field, kwargs[field])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target_dir",
        help="Directory containing files to process",
    )
    parser.add_argument("--outdir", help="Directory to output files to", default=None)
    parser.add_argument("--actors", help="list of actors", nargs="+")
    parser.add_argument("--publisher", default="self-published")

    parser.add_argument(
        "target_files",
        help="Files to process",
        nargs="+",
    )

    parser.add_argument(
        "--execute",
        "Executes, mutating data on disk, if not proided, dryruns",
        action="store_True",
    )

    parser.add_argument("-r", "--recursive")

    args = parser.parse_args()

    # default outdir selection
    if not args.outdir:
        if args.target_dir:
            args.outdir = args.target_dir
        else:
            args.outdir = os.getcwd()

    targets = args.target_files
    if args.recursive:
        for root, dirs, files in os.walk(args.target_dir):
            for file in files:
                targets.append(os.path.join(root, file))

    for target in targets:
        if not os.isfile(target):
            continue

        print(f"Processing: {target}")
        outdir = os.path.join(
            args.outdir, os.path.splitext(os.path.basename(target))[0]
        )
        os.makedirs(
            outdir,
            exist_ok=True,
        )

        extractor = CustomMetadataExtractor(
            actors=args.actors,
            publisher=args.publisher,
        )

        if args.execute():
            shutil.move(target, outdir)
