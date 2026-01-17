import logging

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

log = logging.getLogger("syncer")


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
        diff = await self._fetch_diff_and_print(token, timestamp)
        log.info(f"sync once, new timestamp: {diff.server_timestamp}")
        await self.save_diff(diff)

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

    async def _fetch_diff_and_print(self, token: str, timestamp: int) -> ZmDiffResponse:
        diff = await self._client.fetch_diff(token, timestamp)
        if diff.account:
            log.info(f"found changed {len(diff.account)} accounts {cut_list(diff.account)}")
        if diff.company:
            log.info(f"found changed {len(diff.company)} companies {cut_list(diff.company)}")
        if diff.country:
            log.info(f"found changed {len(diff.country)} countries {cut_list(diff.country)}")
        if diff.instrument:
            log.info(f"found changed {len(diff.instrument)} instruments {cut_list(diff.instrument)}")
        if diff.merchant:
            log.info(f"found changed {len(diff.merchant)} merchants {cut_list(diff.merchant)}")
        if diff.tag:
            log.info(f"found changed {len(diff.tag)} tags {cut_list(diff.tag)}")
        if diff.transaction:
            log.info(f"found changed {len(diff.transaction)} transactions {cut_list(diff.transaction)}")
        if diff.user:
            log.info(f"found changed {len(diff.user)} users {cut_list(diff.user)}")
        return diff


@staticmethod
def cut_list[T](list: list[T]) -> list[T]:
    return list[:3] if len(list) > 3 else list
