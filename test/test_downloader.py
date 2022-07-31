from party_downloader.core import Downloader
import logging, sys
import pytest  # noqa
from pathlib import Path
from party_downloader.models.party_page import PartyPostPage, PartyCreatorPage


@pytest.fixture
def post_page():
    with open(
        Path(__file__).parent / Path("data/post_page.html"), encoding="utf-8"
    ) as f:
        page_data = f.read()
    page = PartyPostPage(
        "https://kemono.party/fantia/user/17779/post/1235253", page_data=page_data
    )
    return page


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


def test_download_post(mocker, post_page, tmp_path):
    mock_download_file = mocker.patch("party_downloader.core.Downloader.download_file")

    downloader = Downloader(tmp_path, True)
    downloader.download_post(post_page)
    args = mock_download_file.call_args_list
    assert str(args[-1][0][0].filename) == "f6184713-c184-48e8-901a-539317502634.jpe"
    assert str(args[0][0][0].filename) == "ff012c63-11be-43cc-bf50-b82ee8779114.jpe"
    assert str(args[1][0][0].filename) == "0386819f-6e2e-41b1-b7d2-47aec07d1f54.jpe"


def test_download_post_existing(mocker, post_page, tmp_path):
    pass


# Need to breadk it down even further to get it to test right
# def test_download_page(mocker, post_page, tmp_path, creator_page):
#     mock_from_url = mocker.patch(
#         "party_downloader.models.party_page.PartyCreatorPage.from_url"
#     )
#     mock_from_url.return_value = creator_page
#     mock_download_post = mocker.patch("party_downloader.core.Downloader.download_post")
#     downloader = Downloader(tmp_path, True)
#     downloader.download_creator("placeholder_url")
#     raise
