from __future__ import annotations

import abc
import dataclasses
import datetime
import decimal
import uuid
from typing import Annotated

import marshmallow_recipe as mr


class CliException(Exception):
    pass


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ZmDiffResponse:
    server_timestamp: int
    transaction: list[ZmTransaction] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ZmTransaction:
    id: uuid.UUID
    user: int
    income: decimal.Decimal
    outcome: decimal.Decimal
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    income_instrument: int
    outcome_instrument: int
    created: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    original_payee: str | None
    deleted: bool
    viewed: bool
    hold: bool | None
    qr_code: str | None
    source: str | None
    income_account: uuid.UUID
    outcome_account: uuid.UUID
    comment: str | None
    payee: str | None
    op_income: decimal.Decimal | None
    op_outcome: decimal.Decimal | None
    op_income_instrument: int | None
    op_outcome_instrument: int | None
    latitude: decimal.Decimal | None
    longitude: decimal.Decimal | None
    merchant: str | None
    income_bank_id: Annotated[str | None, mr.meta(name="incomeBankID")]
    outcome_bank_id: Annotated[str | None, mr.meta(name="outcomeBankID")]
    reminder_marker: uuid.UUID | None

    tag: list[uuid.UUID] | None
    date: datetime.date = dataclasses.field(metadata=mr.datetime_meta(format="%Y-%m-%d"))


class DiffClient(abc.ABC):
    @abc.abstractmethod
    async def fetch_diff(self, server_timestamp: int) -> ZmDiffResponse: ...


class Store(abc.ABC):
    @abc.abstractmethod
    async def get_last_timestamp(self) -> int: ...

    @abc.abstractmethod
    async def save_diff(self, diff: ZmDiffResponse) -> None: ...


class Syncer(abc.ABC):
    @abc.abstractmethod
    async def dry_run(self, timestamp: int, out: str) -> None: ...
    @abc.abstractmethod
    async def sync_once(self) -> None: ...


class NullStore(Store):
    async def get_last_timestamp(self) -> int:
        return 0

    async def save_diff(self, diff: ZmDiffResponse) -> None:
        pass


class NullSyncer(Syncer):
    async def dry_run(self, timestamp: int, out: str) -> None:
        pass

    async def sync_once(self) -> None:
        pass
