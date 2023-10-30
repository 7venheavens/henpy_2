from party_downloader.metadata.extractors.jav_db_extractor import JavDBExtractor
from party_downloader.models.web_data import WebData
from datetime import date
from pathlib import Path
import pytest


@pytest.fixture
def extractor(request):
    with open(
        Path(__file__).parent
        / Path(f"data/metadata_scrapers/javdb/{request.param}.html"),
        encoding="utf-8",
    ) as f:
        page_data = f.read()
    page = WebData(
        f"https://www.javbus.com/en/{request.param[:-3]}", page_data=page_data
    )
    extractor = JavDBExtractor(page)
    return extractor


correct_metadata = {
    "GACHIG-118_en": {
        "id": "GACHIG-118",
        "title": "ありさ\u3000−ヤラレ人形21−",
        "description": "",
        "producer": "",
        "publisher": "Gachinco",
        "studio": "",
        "series": "GachiGOD",
        "actors": ["中野ありさ"],
        "tags": [
            ("c2=146", "Pissing incontinence"),
            ("c3=74", "Shaved"),
            ("c2=9", "Creampie"),
            ("c2=29", "Squirting"),
            ("c4=96", "Cosplay"),
            ("c2=143", "Cum Eating"),
        ],
        "release_date": date(2013, 10, 24),
        "duration": 0,
        "cover_url": "https://c0.jdbstatic.com/covers/5b/5b3ZD.jpg",
        "thumbnail_urls": [],
    },
    "STARS-430_en": {
        "id": "STARS-430",
        "title": "串刺しPtoMレ×プ 大量中出しされた後のマ●コに入った白濁チ●ポで上下穴封鎖！声も出せずに身悶えしかできない美人キャリアウーマンOL 本庄鈴",
        "description": "",
        "producer": "K*WEST",
        "publisher": "SOD Create",
        "studio": "",
        "series": "串刺しPtoMレ×プ",
        "tags": [
            # <span class="value"><a href="/tags?c5=18">Creampie</a>,&nbsp;<a href="/tags?c5=24">3p, 4p</a>,&nbsp;<a href="/tags?c7=28">Solowork</a>,&nbsp;<a href="/tags?c4=65">Slender</a>,&nbsp;<a href="/tags?c5=123">Deep Throating</a>,&nbsp;<a href="/tags?c7=348">Uncensored Crack</a></span>
            ("c5=18", "Creampie"),
            ("c5=24", "3p, 4p"),
            ("c7=28", "Solowork"),
            ("c4=65", "Slender"),
            ("c5=123", "Deep Throating"),
            ("c7=348", "Uncensored Crack"),
        ],
        "actors": ["本庄鈴", "TECH", "ピエール剣", "鮫島", "梅田吉雄"],
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
        print(key)
        assert metadata[key] == val
