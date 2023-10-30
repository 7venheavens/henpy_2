from party_downloader.helpers import is_video
import os
from pathlib import Path
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


def aggregate_files(target_dir, scraper, recursive=False):
    unprocessed = []
    holder = defaultdict(list)
    for root, dirs, filenames in os.walk(target_dir):
        print("filenames:", filenames)
        for filename in filenames:
            # First ensure that the file
            if not is_video(filename):
                print(f"Skipping nonvideo: {filename}")
                continue
            try:
                components = scraper.get_id_components(filename)
                print(scraper, components)
            except (ValueError, AttributeError) as e:
                print(f"Skipping invalid: {filename}, error: {e}")
                unprocessed.append(filename)
                continue
            name, path = components["name"], Path(root) / filename
            holder[name].append((path, components["part"]))

        if not recursive:
            break

    return holder, unprocessed
