from party_downloader.metadata.extractors.avbase_extractor import AVBaseExtractor
from party_downloader.models.web_data import WebData
from datetime import date
import pytest
from pathlib import Path


@pytest.fixture
def extractor(request):
    with open(
        Path(__file__).parent
        / Path(f"data/metadata_scrapers/avbase/{request.param}.html"),
        encoding="utf-8",
    ) as f:
        page_data = f.read()
    page = WebData(
        f"https://db.msin.jp/page/movie?id={request.param}", page_data=page_data
    )
    extractor = AVBaseExtractor(page)
    return extractor


correct_metadata = {
    "ncy150": {
        "id": "NCY150",
        "title": "学校卒業→初撮り成功【小さなお口が裂ける巨根チ〇ポを捻じ込み初体験イラマチオ】Ｄキス唾液交尾・パイパン淫具拡張アクメ責め【ミニマム低身長＆宅コスレイヤー18歳の思春期ボディ】ベロ舐め調教ドキュメント",
        "description": "",
        "producer": "全日本カメコ協同組合",
        "publisher": "",
        "studio": "",
        "series": "",
        "actors": ["七咲みいろ"],
        "tags": [
            ("着衣エッチ", "着衣エッチ"),
            ("フェラ", "フェラ"),
            ("調教", "調教"),
            ("フェチ", "フェチ"),
            ("スレンダー", "スレンダー"),
            ("口内射精", "口内射精"),
            ("おっぱい", "おっぱい"),
            ("鬼畜", "鬼畜"),
            ("お嬢様", "お嬢様"),
            ("美少女", "美少女"),
            ("ツンデレ", "ツンデレ"),
            ("コスプレ動画", "コスプレ動画"),
            ("マゾ", "マゾ"),
            ("ミニマム", "ミニマム"),
            ("強気・勝気", "強気・勝気"),
        ],
        "release_date": date(2022, 5, 15),
        "duration": 0,
        "cover_url": "https://dl.getchu.com/data/item_img/40416/4041698/4041698top.jpg",
        "thumbnail_urls": [],
    },
    "VRKM-1213": {
        "id": "VRKM-1213",
        "title": "【VR】親が決めた結婚相手は女子校生！？ 見せつけ誘惑ナマ乳首で献身的に距離を詰めてくるドキドキ中出し性交 百咲みいろ",
        "description": "",
        "producer": "ケイ・エム・プロデュース",
        "publisher": "KMPVR",
        "studio": "",
        "series": "",
        "actors": ["百咲みいろ"],
        "tags": [
            # Convert the following: 単体作品 ハイクオリティVR VR専用 騎乗位 胸チラ ノーブラ 美少女 中出し
            ("単体作品", "単体作品"),
            ("ハイクオリティVR", "ハイクオリティVR"),
            ("VR専用", "VR専用"),
            ("騎乗位", "騎乗位"),
            ("胸チラ", "胸チラ"),
            ("ノーブラ", "ノーブラ"),
            ("美少女", "美少女"),
            ("中出し", "中出し"),
        ],
        "release_date": date(2023, 11, 25),
        "duration": 80 * 60,
        "cover_url": "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213pl.jpg",
        "thumbnail_urls": [
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-1.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-2.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-3.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-4.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-5.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-6.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-7.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-8.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-9.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-10.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-11.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-12.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-13.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-14.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-15.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-16.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-17.jpg",
            "https://pics.dmm.co.jp/digital/video/vrkm01213/vrkm01213jp-18.jpg",
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
