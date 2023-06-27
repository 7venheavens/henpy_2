"""Scripts to handle bulk annotation of videos which might not have existing metadata
"""
import argparse
from party_downloader.metadata.extractors import BaseMetadataExtractor
import os
import shutil
import re


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
        "--target_files",
        help="Files to process",
        nargs="+",
    )

    parser.add_argument(
        "--execute",
        help="Executes, mutating data on disk, if not proided, dryruns",
        action="store_true",
    )
    parser.add_argument("-r", "--recursive")
    parser.add_argument(
        "--id_regex", help="Regex to extract id from filename", default=r"\w+"
    )
    parser.add_argument(
        "--title-regex", help="Regex to extract title from filename", default=None
    )

    parser.add_argument("--nameflags", default="")

    args = parser.parse_args()

    # default outdir selection
    if not args.outdir:
        if args.target_dir:
            args.outdir = args.target_dir
        else:
            args.outdir = os.getcwd()

    if not args.title_regex:
        args.title_regex = args.id_regex

    targets = args.target_files or []
    for root, dirs, files in os.walk(args.target_dir):
        for file in files:
            targets.append(os.path.join(root, file))
        if not args.recursive:
            break

    print(f"processing: {targets}")

    for target in targets:
        if not os.path.isfile(target):
            continue

        print(f"Processing: {target}")

        id = re.search(args.id_regex, os.path.basename(target)).group(1)
        title = re.search(args.title_regex, os.path.basename(target)).group(1)
        if "replace_underscores" in args.nameflags:
            title = title.replace("_", " ")

        if args.publisher:
            outname = f"{args.publisher} - {id}"
        else:
            outname = id

        extractor = CustomMetadataExtractor(
            id=id,
            title=title,
            actors=args.actors,
            publisher=args.publisher,
        )

        outdir = os.path.join(args.outdir, outname)
        os.makedirs(
            outdir,
            exist_ok=True,
        )
        outpath = os.path.join(outdir, f"{outname}{os.path.splitext(target)[1]}")
        print(f"File: {target} -> {outpath}")
        print(f"Extracted metadata: {extractor.__dict__}")
        with open(os.path.splitext(outpath)[0] + ".nfo", "w") as f:
            f.write(extractor.metadata_nfo)
        if args.execute:
            shutil.move(target, outpath)
