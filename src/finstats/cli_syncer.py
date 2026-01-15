from pathlib import Path
from types import TracebackType
from typing import Self

import sqlalchemy.ext.asyncio as sa_async

from finstats.client import ZenMoneyClient
from finstats.contracts import ZmDiffResponse
from finstats.file import parse_and_validate_path, write_content_to_file
from finstats.store.accounts import AccountsRepository
from finstats.store.base import create_engine
from finstats.store.companies import CompaniesRepository
from finstats.store.connection import ConnectionScope
from finstats.store.countries import CountriesRepository
from finstats.store.instruments import InstrumentsRepository
from finstats.store.merchants import MerchantsRepository
from finstats.store.tags import TagsRepository
from finstats.store.timestamp import TimestampRepository
from finstats.store.transactions import TransactionsRepository
from finstats.store.users import UsersRepository


class CliSyncer:
    _client: ZenMoneyClient
    _engine: sa_async.AsyncEngine
    _token: str

    def __init__(self, token: str) -> None:
        self._token = token

    async def __aenter__(self) -> Self:
        self._engine = create_engine()
        self._connection_scope = ConnectionScope(self._engine)
        self._accounts_repository = AccountsRepository(self._connection_scope)
        self._companies_repository = CompaniesRepository(self._connection_scope)
        self._countries_repository = CountriesRepository(self._connection_scope)
        self._instruments_repository = InstrumentsRepository(self._connection_scope)
        self._merchants_repository = MerchantsRepository(self._connection_scope)
        self._tags_repository = TagsRepository(self._connection_scope)
        self._timestamp_repository = TimestampRepository(self._connection_scope)
        self._transactions_repository = TransactionsRepository(self._connection_scope)
        self._users_repository = UsersRepository(self._connection_scope)

        self._client = ZenMoneyClient()
        self._client.create_session()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._engine is not None:
            await self._engine.dispose()
        if self._client is not None:
            await self._client.dispose()

    async def dry_run(self, timestamp: int, out: str) -> None:
        path = parse_and_validate_path(out)
        diff = await self._fetch_diff_and_print(timestamp)
        write_content_to_file(path, diff)

    async def sync_once(self) -> None:
        timestamp = await self._timestamp_repository.get_last_timestamp()
        print(f"sync once, timestamp: {timestamp}")
        diff = await self._fetch_diff_and_print(timestamp)
        write_content_to_file(Path("file.json"), diff)
        await self.save_diff(diff)

    async def _fetch_diff_and_print(self, timestamp: int) -> ZmDiffResponse:
        diff = await self._client.fetch_diff(self._token, timestamp)
        print(
            f"transactions: {len(diff.transaction)}, "
            f"deleted: {sum(t.deleted for t in diff.transaction)}, "
            f"new: {sum(not t.deleted and not t.viewed for t in diff.transaction)}"
        )
        return diff

    async def save_diff(self, diff: ZmDiffResponse) -> None:
        async with self._connection_scope.acquire():
            await self._timestamp_repository.save_last_timestamp(diff.server_timestamp)
            await self._accounts_repository.save_accounts(diff.account)
            await self._companies_repository.save_companies(diff.company)
            await self._countries_repository.save_countries(diff.country)
            await self._instruments_repository.save_instruments(diff.instrument)
            await self._merchants_repository.save_merchants(diff.merchant)
            await self._tags_repository.save_tags(diff.tag)
            for transaction in diff.transaction:
                await self._transactions_repository.save_transactions([transaction])
            await self._users_repository.save_users(diff.user)
