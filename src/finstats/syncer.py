import logging

from finstats.client.client import ZenMoneyClient
from finstats.contracts import Transaction, ZenmoneyDiff
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


class Syncer:
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
        await self.save_diff(diff)

    async def sync_diff(self, token: str, transactions: list[Transaction]) -> ZenmoneyDiff:
        timestamp = await self._timestamp_repository.get_last_timestamp()
        diff = await self._sync_and_print(
            token=token,
            request=ZenmoneyDiff(server_timestamp=timestamp, transactions=transactions),
        )
        await self.save_diff(diff)
        return diff

    async def save_diff(self, diff: ZenmoneyDiff) -> None:
        async with self._connection_scope.acquire():
            await self._timestamp_repository.save_last_timestamp(diff.server_timestamp)
            await self._accounts_repository.save_accounts(diff.accounts)
            await self._companies_repository.save_companies(diff.companies)
            await self._countries_repository.save_countries(diff.countries)
            await self._instruments_repository.save_instruments(diff.instruments)
            await self._merchants_repository.save_merchants(diff.merchants)
            await self._tags_repository.save_tags(diff.tags)
            for transaction in diff.transactions:
                await self._transactions_repository.save_transactions([transaction])
            await self._users_repository.save_users(diff.users)

    async def _fetch_diff_and_print(self, token: str, timestamp: int) -> ZenmoneyDiff:
        return await self._sync_and_print(
            token=token,
            request=ZenmoneyDiff(server_timestamp=timestamp),
        )

    async def _sync_and_print(self, token: str, request: ZenmoneyDiff) -> ZenmoneyDiff:
        diff = await self._client.sync_diff(token=token, diff=request)
        log.info("sync, new timestamp: %s", diff.server_timestamp)
        if diff.accounts:
            log.info("found changed %d accounts %s", len(diff.accounts), self.cut_list(diff.accounts))
        if diff.companies:
            log.info("found changed %d companies %s", len(diff.companies), self.cut_list(diff.companies))
        if diff.countries:
            log.info("found changed %d countries %s", len(diff.countries), self.cut_list(diff.countries))
        if diff.instruments:
            log.info("found changed %d instruments %s", len(diff.instruments), self.cut_list(diff.instruments))
        if diff.merchants:
            log.info("found changed %d merchants %s", len(diff.merchants), self.cut_list(diff.merchants))
        if diff.tags:
            log.info("found changed %d tags %s", len(diff.tags), self.cut_list(diff.tags))
        if diff.transactions:
            log.info("found changed %d transactions %s", len(diff.transactions), self.cut_list(diff.transactions))
        if diff.users:
            log.info("found changed %d users %s", len(diff.users), self.cut_list(diff.users))
        return diff

    @staticmethod
    def cut_list[T](items: list[T]) -> list[T]:
        return items[:3] if len(items) > 3 else items
