from party_downloader.metadata.extractors.msin_extractor import MSINExtractor
from party_downloader.models.web_data import WebData
from datetime import date
import pytest
from pathlib import Path


@pytest.fixture
def extractor(request):
    with open(
        Path(__file__).parent
        / Path(f"data/metadata_scrapers/msin/{request.param}.html"),
        encoding="utf-8",
    ) as f:
        page_data = f.read()
    page = WebData(
        f"https://db.msin.jp/page/movie?id={request.param}", page_data=page_data
    )
    extractor = MSINExtractor(page)
    return extractor


correct_metadata = {
    "2538802": {
        "id": "fc2-ppv-3104128",
        "title": "【限定値下げ中】正真正銘初撮りの原石！地味巨乳JD娘に生中出し。こんな子とできるなんて。 FC2-PPV-3104128",
        "description": "",
        "producer": "ギガ珍太郎",
        "publisher": "FC2 アダルト コンテンツマーケット",
        "studio": "",
        "series": "",
        "actors": [],
        "tags": [
            ("ハメ撮り", "ハメ撮り"),
            ("素人", "素人"),
            ("美乳", "美乳"),
            ("中出し", "中出し"),
            ("個人撮影", "個人撮影"),
            ("フェラ", "フェラ"),
            ("オリジナル", "オリジナル"),
            ("かわいい", "かわいい"),
            ("女子大生", "女子大生"),
        ],
        "release_date": date(2022, 10, 3),
        "duration": 4355,
        "cover_url": "https://img.msin.info/images/cover/fc2/fc2-ppv-3104128.jpg",
        "thumbnail_urls": [
            "https://storage71000.contents.fc2.com/file/367/36679264/1664518411.96.jpg",
            "https://storage71000.contents.fc2.com/file/367/36679264/1664518412.23.jpg",
            "https://storage71000.contents.fc2.com/file/367/36679264/1664518412.5.jpg",
            "https://storage71000.contents.fc2.com/file/367/36679264/1664518412.78.jpg",
            "https://storage71000.contents.fc2.com/file/367/36679264/1664518413.03.jpg",
            "https://storage71000.contents.fc2.com/file/367/36679264/1664518413.3.jpg",
            "https://storage71000.contents.fc2.com/file/367/36679264/1664518413.57.jpg",
            "https://storage71000.contents.fc2.com/file/367/36679264/1664518413.83.jpg",
            "https://storage70000.contents.fc2.com/file/367/36679264/1664518677.96.jpg",
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
        print(key, val, metadata[key])
        assert metadata[key] == val
