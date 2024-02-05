from party_downloader.metadata.scrapers.avbase_scraper import AVBaseScraper
import pytest
import re
from pathlib import Path
from party_downloader.models.web_data import WebData

expected = {"id": "30762971", "name": "30762971", "part": None}


@pytest.fixture
def search_single_result():
    with open(
        Path(__file__).parent.parent.parent.parent
        / Path(f"data/metadata_scrapers/avbase/search_result_single_ncy150.html"),
        encoding="utf-8",
    ) as f:
        page_data = f.read()
    return WebData("https://www.avbase.net/works?q=ncy150", page_data)


@pytest.fixture
def search_multiple_result():
    with open(
        Path(__file__).parent.parent.parent.parent
        / Path(f"data/metadata_scrapers/avbase/search_result_multiple.html"),
        encoding="utf-8",
    ) as f:
        page_data = f.read()
    return WebData("https://www.avbase.net/works?q=ncy150", page_data)


def test_is_multiple_for_single_result(search_single_result):
    scraper = AVBaseScraper()
    assert not scraper.is_multiple(search_single_result)


def test_is_multiple_for_multiple_result(search_multiple_result):
    scraper = AVBaseScraper()
    assert scraper.is_multiple(search_multiple_result)


def test_get_target_from_single_result(search_single_result):
    scraper = AVBaseScraper()
    res = scraper.get_target_from_single_result(search_single_result)
    assert res == "/works/NCY150"
