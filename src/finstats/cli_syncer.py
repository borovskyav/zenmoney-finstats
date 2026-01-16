from pathlib import Path

import sqlalchemy.ext.asyncio as sa_async

from finstats.client import ZenMoneyClient
from finstats.contracts import ZmDiffResponse
from finstats.file import parse_and_validate_path, write_content_to_file
from finstats.store import (
    AccountsRepository,
    CompaniesRepository,
    CountriesRepository,
    InstrumentsRepository,
    MerchantsRepository,
    TagsRepository,
    TimestampRepository,
    TransactionsRepository,
    UsersRepository,
)
from finstats.store.connection import ConnectionScope


class CliSyncer:
    _client: ZenMoneyClient
    _engine: sa_async.AsyncEngine

    def __init__(
        self,
        connection_scope: ConnectionScope,
        accounts_repository: AccountsRepository,
        companies_repository: CompaniesRepository,
        countries_repository: CountriesRepository,
        instruments_repository: InstrumentsRepository,
        merchants_repository: MerchantsRepository,
        tags_repository: TagsRepository,
        timestamp_repository: TimestampRepository,
        transactions_repository: TransactionsRepository,
        users_repository: UsersRepository,
        zm_client: ZenMoneyClient,
    ) -> None:
        self._connection_scope = connection_scope
        self._accounts_repository = accounts_repository
        self._companies_repository = companies_repository
        self._countries_repository = countries_repository
        self._instruments_repository = instruments_repository
        self._merchants_repository = merchants_repository
        self._tags_repository = tags_repository
        self._timestamp_repository = timestamp_repository
        self._transactions_repository = transactions_repository
        self._users_repository = users_repository
        self._client = zm_client

    async def dry_run(self, token: str, timestamp: int, out: str) -> None:
        path = parse_and_validate_path(out)
        diff = await self._fetch_diff_and_print(token, timestamp)
        write_content_to_file(path, diff)

    async def sync_once(self, token: str) -> None:
        timestamp = await self._timestamp_repository.get_last_timestamp()
        print(f"sync once, timestamp: {timestamp}")
        diff = await self._fetch_diff_and_print(token, timestamp)
        write_content_to_file(Path("file.json"), diff)
        await self.save_diff(diff)

    async def _fetch_diff_and_print(self, token: str, timestamp: int) -> ZmDiffResponse:
        diff = await self._client.fetch_diff(token, timestamp)
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
