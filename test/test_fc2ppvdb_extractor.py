from party_downloader.metadata.extractors import FC2PPVDBExtractor
from party_downloader.models.web_data import WebData
from datetime import date
import pytest
from pathlib import Path


@pytest.fixture
def extractor(request):
    with open(
        Path(__file__).parent
        / Path(f"data/metadata_scrapers/fc2ppvdb/{request.param}.html"),
        encoding="utf-8",
    ) as f:
        page_data = f.read()
    page = WebData(
        f"https://adult.contents.fc2.com/article/{request.param}", page_data=page_data
    )
    extractor = FC2PPVDBExtractor(page)
    return extractor


correct_metadata = {
    "4540239": {
        "id": "FC2-PPV-4540239",
        "title": "FC2PPV-4540239 【絶叫全力チャレンジ×KAWAII女子大生】※特典にて過去1大絶叫のアナルSEX付き アイドル級の透明感を誇る女子大生すずちゃん。生ハメで想像を超える巨根に経験の少ないすずちゃん喘・ぎ・狂・う",
        "description": "",
        "producer": "変態紳士倶楽部",
        "publisher": "",
        "studio": "",
        "series": "",
        "actors": [],
        "tags": [
            ("ハメ撮り", "ハメ撮り"),
            ("中出し", "中出し"),
            ("個人撮影", "個人撮影"),
            ("アナル", "アナル"),
            ("色白", "色白"),
            ("アイドル", "アイドル"),
            ("清楚", "清楚"),
            ("顔出し", "顔出し"),
            ("巨根", "巨根"),
            ("18歳", "18歳"),
        ],
        "release_date": date(2024, 9, 21),
        "duration": 3055,
        "cover_url": "https://www.fc2ppvdb.com/storage/images/article/004/54/fc2ppv-4540239.jpg",
        "thumbnail_urls": [],
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
