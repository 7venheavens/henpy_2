from party_downloader.metadata.scrapers.base_metadata_scraper import BaseMetadataScraper
import pytest
import re

expected = {"id": "30762971", "name": "30762971", "part": None}


@pytest.mark.parametrize(
    "text,expected",
    [
        ("30762971", expected),
        (
            "30762971_2",
            {"id": "30762971", "name": "30762971", "part": "2"},
        ),
    ],
)
def test_base_metadata_scraper_get_id_components(text, expected):
    class TestScraper(BaseMetadataScraper):
        COMPONENT_REGEX = re.compile("(\d+)(?:_(\d+))?")

    assert TestScraper.get_id_components(text) == expected
