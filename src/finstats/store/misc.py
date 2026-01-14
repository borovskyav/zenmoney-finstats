import dataclasses
from collections.abc import Sequence
from typing import Any, get_origin

import sqlalchemy as sa

__field_names: dict[type, tuple[str, ...]] = {}


def from_dataclass[T](cls: T) -> dict[str, Any]:
    if not dataclasses.is_dataclass(cls) or isinstance(cls, type):
        raise TypeError("content must be a dataclass instance")

    return dataclasses.asdict(cls)


def from_dataclasses[T](cls: Sequence[T]) -> Sequence[dict[str, Any]]:
    return [from_dataclass(c) for c in cls]


def to_dataclass[T](cls: type[T], row: sa.Row) -> T:
    field_names = __field_names.get(cls)
    if not field_names:
        effective_cls = get_origin(cls) or cls
        field_names = tuple(field.name for field in dataclasses.fields(effective_cls))
        __field_names[cls] = field_names

    return cls(**{field_name: getattr(row, field_name) for field_name in field_names})


def to_dataclasses[T](cls: type[T], rows: Sequence[sa.Row]) -> list[T]:
    return [to_dataclass(cls, row) for row in rows]
