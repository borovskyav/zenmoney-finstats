import re
from pathlib import Path

import pytest

from finstats.cli import CliException, parse_and_validate_path


@pytest.mark.parametrize(
    "raw, expected_message",
    [
        pytest.param(r".\data.json", "--out must not start with .\\, insure using ./", id="backslash on start"),
    ],
)
def test_parse_and_validate_path_invalid_should_raise_exception(raw: str, expected_message: str) -> None:
    with pytest.raises(CliException, match=re.escape(expected_message)):
        parse_and_validate_path(raw)


@pytest.mark.parametrize(
    "raw, expected_name, parent",
    [
        pytest.param(r"data.json", r"data.json", Path("."), id="simple"),
        pytest.param(r"./data.json", r"data.json", Path("."), id="with dot"),
        pytest.param(r"/data.json", r"data.json", Path("/"), id="slash without dot"),
        pytest.param(r"~/data.json", r"data.json", Path("~"), id="home directory"),
        pytest.param(r"../data.json", r"data.json", Path(".."), id="with double dot"),
        pytest.param(r"./data\data.json", r"data\data.json", Path("."), id="backslash in the middle"),
    ],
)
def test_parse_and_validate_path_valid(raw: str, expected_name: str, parent: Path) -> None:
    p = parse_and_validate_path(raw)
    assert p.name == expected_name
    assert p.parent == parent
    assert p.suffix == ".json"
