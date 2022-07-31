from party_downloader.core import PartyCreatorPage
import pytest
from pathlib import Path
from urllib.parse import urlparse


@pytest.fixture
def creator_page():
    with open(
        Path(__file__).parent / Path("data/creator_page.html"), encoding="utf-8"
    ) as f:
        page_data = f.read()
    page = PartyCreatorPage(
        "https://kemono.party/fantia/user/17779", page_data=page_data
    )
    return page


# def test_get_download_metadata(creator_page):
#     data = list(creator_page.get_download_metadata())
# Need to patch out the method, or it'll hit the web
# Check for a download
# assert any(
#     datum.path
#     == "https://kemono.party/data/ec/93/ec934ef6c4d8dccf89ad096f06c2c5c68347c2140a7770c55b9306b9e4c9a770.mp4?f=mako202204_5.mp4"
#     and datum.target_dir == Path("fantia/17779/1235253")
#     and datum.filename == "mako202204_5.mp4"
#     for datum in data
# )


# def test_get_next_page(creator_page):
#     assert creator_page.next_page_url == "https://kemono.party/fantia/user/17779?o=25"


def test_pages(creator_page):
    pages = list(creator_page.pages)
    offsets = [page.parsed_url.query for page in pages]
    # test that it's going in reverse order
    assert offsets == [f"o={offset}" for offset in range(850, -1, -25)]
    assert pages[0].parsed_url.netloc == "kemono.party"
    assert pages[0].parsed_url.scheme == "https"


def test_get_child_posts(creator_page):
    pass
