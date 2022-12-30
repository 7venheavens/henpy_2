from party_downloader.models.metadata.extractors.javbus_extractor import JavBusExtractor
from party_downloader.models.web_data import WebData
from datetime import date
from pathlib import Path
import pytest


@pytest.fixture
def extractor(request):
    with open(
        Path(__file__).parent
        / Path(f"data/metadata_scrapers/javbus/{request.param}.html"),
        encoding="utf-8",
    ) as f:
        page_data = f.read()
    page = WebData(
        f"https://www.javbus.com/en/{request.param[:-3]}", page_data=page_data
    )
    extractor = JavBusExtractor(page)
    return extractor


correct_metadata = {
    "SCR-304_en": {
        "id": "SCR-304",
        "title": "SCR-304 欲望に囚われた父親に犯●れる一人娘猥褻近親相姦映像",
        "description": "",
        "producer": "",
        "publisher": "グレイズ",
        "studio": "S-CRIME",
        "series": "",
        "actors": [],
        "tags": [
            ("3f", "Deep Throat"),
            ("3r", "Rough Sex"),
            ("20", "Incest"),
            ("e7", "娘・養女"),
            ("3k", "Short & Petite"),
            ("30", "Beautiful Girl"),
            ("83", "Mini series"),
            ("4o", "Hi-Def"),
            ("4", "Creampie"),
            ("22", "Shaved Pussy"),
            ("t", "Small Tits"),
        ],
        "release_date": date(2022, 12, 5),
        "duration": 120,
        "cover_url": "https://www.javbus.com/pics/cover/9efw_b.jpg",
        "thumbnail_urls": [
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-1.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-2.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-3.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-4.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-5.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-6.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-7.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-8.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-9.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-10.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-11.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-12.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-13.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-14.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-15.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-16.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-17.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-18.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-19.jpg",
            "https://pics.dmm.co.jp/digital/video/12scr00304/12scr00304jp-20.jpg",
        ],
    },
    "STARS-430_en": {
        "id": "STARS-430",
        "title": "STARS-430 串刺しPtoMレ×プ 大量中出しされた後のマ●コに入った白濁チ●ポで上下穴封…",
        "description": "",
        "producer": "K*WEST",
        "publisher": "SODクリエイト",
        "studio": "SODstar",
        "series": "",
        "tags": [
            ("3f", "Deep Throat"),
            ("1f", "Slender"),
            ("4", "Creampie"),
        ],
    },
}


@pytest.mark.parametrize(
    "extractor, expected_metadata",
    [
        (extractor, expected_metadata)
        for extractor, expected_metadata in correct_metadata.items()
    ],
    indirect=["extractor"],
)
def test_extractor(extractor, expected_metadata):
    metadata = extractor.metadata
    # Allow for partials as whole might be too time consuming to handle
    for key, val in expected_metadata.items():
        assert metadata[key] == val
