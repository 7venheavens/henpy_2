from party_downloader.core import PartyPostPage
import pytest
from pathlib import Path


@pytest.fixture
def post_page():
    with open(Path(__file__).parent / Path("data/post_page.html"), encoding="utf-8") as f:
        page_data = f.read()
    page = PartyPostPage("https://kemono.party/fantia/user/17779/post/1235253", page_data=page_data)
    return page


# def test_get_download_metadata(post_page):

#     data = list(post_page.get_download_metadata())
#     # Check for a download
#     assert any(
#         datum.path
#         == "https://kemono.party/data/ec/93/ec934ef6c4d8dccf89ad096f06c2c5c68347c2140a7770c55b9306b9e4c9a770.mp4?f=mako202204_5.mp4"
#         and datum.target_dir == Path("fantia/17779/1235253")
#         and datum.filename == "mako202204_5.mp4"
#         for datum in data
#     )
#     # check for an image
