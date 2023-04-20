import pytest
import json
import requests

from party_downloader.metadata.dumpers.base_metadata_dumper import BaseMetadataDumper


class Dumper(BaseMetadataDumper):
    def get_query_string(self, file_name: str) -> str:
        return file_name


@pytest.fixture
def previous_run_setup(tmp_path):
    run_json = tmp_path / "run.json"
    run_json.write_text(
        json.dumps(
            {
                "dump_name": "test_dump.html",
                "url": "https://www.test.com",
            }
        )
    )
    dump = tmp_path / "test_dump.html"
    dump.write_text("<html><body>test</body></html>")
    return tmp_path


def test_prepare_extractor_no_previous_run(tmp_path, mocker):
    mocker.patch("requests.get", return_value=requests.Response())
    Dumper().prepare_extractor(tmp_path / "test.mp4")
    requests.get.assert_called_once()


def test_prepare_extractor(tmp_path, previous_run_setup, mocker):
    mocker.patch("requests.get")
    extractor = Dumper().prepare_extractor(tmp_path / "test.mp4")
    assert extractor.webdata.parsed_url.geturl() == "https://www.test.com"
    requests.get.assert_not_called()
