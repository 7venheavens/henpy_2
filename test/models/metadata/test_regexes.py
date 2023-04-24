import pytest
from party_downloader.helpers import Regexes

expected = "3076297"


@pytest.mark.parametrize(
    "text,expected",
    [
        ("FC2_PPV_3076297_2", (expected, "2")),
        ("FC2-PPV-3076297", (expected, "")),
        ("fc2-ppv-3076297", (expected, "")),
    ],
)
def test_fc2_regex(text, expected):
    assert Regexes.FC2.match(text).group(1) == expected[0]
