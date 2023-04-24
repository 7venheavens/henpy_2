import pytest
from party_downloader.metadata.aggregate import aggregate_files
from party_downloader.metadata.scrapers.fc2_scraper import FC2Scraper
import os


def test_aggregation(tmp_path):
    dir = tmp_path / "dir"
    dir.mkdir()
    # normal files
    (dir / "fc2-ppv-1231232.mp4").touch()
    # Split files
    (dir / "fc2-ppv-1231233_1.mp4").touch()
    (dir / "fc2-ppv-1231233_2.mp4").touch()
    # Invalid files
    (dir / "sdaflkasdlkfas.mp4").touch()
    assert len(os.listdir(dir)) == 4

    batched, unprocessed = aggregate_files(dir, FC2Scraper)
    assert len(batched["fc2-ppv-1231232"]) == 1
    assert len(batched["fc2-ppv-1231233"]) == 2
    assert len(unprocessed) == 1
    assert unprocessed[0] == "sdaflkasdlkfas.mp4"
