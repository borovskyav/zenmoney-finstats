# checks if a given variable is valid path
import dataclasses
import json
from pathlib import Path

import marshmallow_recipe as mr

from finstats.contracts import CliException


def parse_and_validate_path(raw: str) -> Path:
    if raw == "":
        raise CliException("--out path is empty")

    if "\x00" in raw:
        raise CliException("--out path contains NUL byte")

    if raw.startswith(".\\"):
        raise CliException("--out must not start with .\\, insure using ./")

    if raw.endswith(("/", "\\")):
        raise CliException("--out path looks like a directory, expected a .json file path")

    p = Path(raw)

    if p.suffix.lower() != ".json":
        raise CliException(f"Expected .json file path, got: {p}")

    return p


def write_content_to_file(path: Path, content: object) -> None:
    if not dataclasses.is_dataclass(content) or isinstance(content, type):
        raise TypeError("content must be a dataclass instance")

    content_str = json.dumps(mr.dump(content), separators=(",", ":"), ensure_ascii=False, indent=4)

    if path.exists() and not path.is_file():
        raise CliException(f"Output path exists but is not a file: {path}")

    parent = path.parent
    if parent != Path("."):
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            CliException(f"Output path exists but is not a directory: {path}")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content_str)
        f.write("\n")
