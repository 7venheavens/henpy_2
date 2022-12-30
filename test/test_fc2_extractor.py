from party_downloader.metadata.extractors.fc2_extractor import FC2Extractor
from party_downloader.models.web_data import WebData
from datetime import date
import pytest
from pathlib import Path


@pytest.fixture
def extractor(request):
    with open(
        Path(__file__).parent
        / Path(f"data/metadata_scrapers/fc2/{request.param}.html"),
        encoding="utf-8",
    ) as f:
        page_data = f.read()
    page = WebData(
        f"https://adult.contents.fc2.com/article/{request.param}", page_data=page_data
    )
    extractor = FC2Extractor(page)
    return extractor


correct_metadata = {
    "3104128": {
        "id": "FC2-PPV-3104128",
        "title": "正真正銘初撮りの原石！地味巨乳JD娘に生中出し。こんな子とできるなんて。",
        "description": "",
        "producer": "ギガ珍太郎",
        "publisher": "",
        "studio": "",
        "series": "",
        "actors": [],
        "tags": [
            ("%E3%83%8F%E3%83%A1%E6%92%AE%E3%82%8A", "ハメ撮り"),
            ("%E7%B4%A0%E4%BA%BA", "素人"),
            ("%E7%BE%8E%E4%B9%B3", "美乳"),
            ("%E4%B8%AD%E5%87%BA%E3%81%97", "中出し"),
            ("%E5%80%8B%E4%BA%BA%E6%92%AE%E5%BD%B1", "個人撮影"),
            ("%E3%83%95%E3%82%A7%E3%83%A9", "フェラ"),
            ("%E3%82%AA%E3%83%AA%E3%82%B8%E3%83%8A%E3%83%AB", "オリジナル"),
            ("%E3%81%8B%E3%82%8F%E3%81%84%E3%81%84", "かわいい"),
            ("%E5%A5%B3%E5%AD%90%E5%A4%A7%E7%94%9F", "女子大生"),
        ],
        "release_date": date(2022, 10, 3),
        "duration": 4355,
        "cover_url": "https://contents-thumbnail2.fc2.com/w276/storage71000.contents.fc2.com/file/367/36679264/1664518411.89.jpg",
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
        assert metadata[key] == val
