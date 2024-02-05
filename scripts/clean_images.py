from __future__ import annotations
import os
from party_downloader.helpers import make_folder_from_fanart
from datetime import datetime
from pathlib import Path
import shutil
import argparse


def get_candidates(folder: str | Path, min_dt: datetime):
    candidates = []
    for root, dirs, files in os.walk(folder):
        for num, dir in enumerate(dirs, 1):
            if num % 100 == 0:
                print(f"Processed {num} directories, Last={dir}")
            ts = os.path.getmtime(os.path.join(root, dir))
            dt = datetime.fromtimestamp(ts)
            if dt < min_dt:
                continue
            # Do the cleaning and checks
            # Ensure that there isn't both a folder.jpg and a fanart.jpg
            if os.path.exists(os.path.join(root, dir, "folder.jpg")) and os.path.exists(
                os.path.join(root, dir, "fanart.jpg")
            ):
                continue
            candidates.append(Path(root) / dir)
        break
    return candidates


def clean_images(folder: str | Path, execute=False):
    print("Processing: ", folder)
    # Create the folder as a fanart first, then swap
    assert os.path.exists(folder)
    if (
        not (Path(folder) / "folder.jpg").exists()
        ^ (Path(folder) / "fanart.jpg").exists()
    ):
        return
    target = Path(folder) / "folder.jpg"
    output = Path(folder) / "fanart.jpg"
    if not target.exists():
        target = Path(folder) / "fanart.jpg"
        output = Path(folder) / "folder.jpg"
    intermediate = Path(folder) / "intermediate.jpg"
    if execute:
        make_folder_from_fanart(target, output)
        # Swapt the two files if the raw data was folder.jpg
        if target.name.endswith("folder.jpg"):
            shutil.move(target, intermediate)
            shutil.move(output, target)
            shutil.move(intermediate, output)
    else:
        if target.name.endswith("folder.jpg"):
            print(f"Would move {output} to {target}, swapping files")
        else:
            print(f"Would move {target} to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "target_dir",
        type=str,
        help="directory containing the various subdirectories to clean",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute the cleaning",
        default=False,
    )
    args = parser.parse_args()
    candidates = get_candidates(args.target_dir, datetime(2021, 1, 1))
    print(f"Found {len(candidates)} candidates", candidates[:5])
    for candidate in candidates:
        clean_images(candidate, args.execute)
