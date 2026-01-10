import datetime
from collections.abc import Iterable
from typing import Any

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_async
from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.contracts import (
    ZmAccount,
    ZmCompany,
    ZmCountry,
    ZmDiffResponse,
    ZmInstrument,
    ZmMerchant,
    ZmTag,
    ZmTransaction,
    ZmUser,
)
from finstats.store.base import (
    AccountTable,
    CompanyTable,
    CountryTable,
    InstrumentTable,
    MerchantTable,
    TagTable,
    TimestampTable,
    TransactionsTable,
    UserTable,
)


async def get_last_timestamp(connection: sa_async.AsyncConnection) -> int:
    stmt = sa.select(TimestampTable.last_synced_timestamp).where(TimestampTable.id == 1)
    result = await connection.execute(stmt)
    ts = result.scalar_one()
    return int(ts.timestamp())


async def save_diff(connection: sa_async.AsyncConnection, diff: ZmDiffResponse) -> None:
    await save_last_timestamp(connection, diff.server_timestamp)
    await save_accounts(connection, diff.account)
    await save_companies(connection, diff.company)
    await save_countries(connection, diff.country)
    await save_instruments(connection, diff.instrument)
    await save_merchants(connection, diff.merchant)
    await save_tags(connection, diff.tag)
    await save_transactions(connection, diff.transaction)
    await save_users(connection, diff.user)


async def save_last_timestamp(connection: sa_async.AsyncConnection, timestamp: int) -> None:
    dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.UTC)
    stmt = sa.update(TimestampTable).where(TimestampTable.id == 1).values(last_synced_timestamp=dt)
    await connection.execute(stmt)


async def save_accounts(connection: sa_async.AsyncConnection, accounts: list[ZmAccount]) -> None:
    if not accounts:
        return

    stmt = sa_postgresql.insert(AccountTable).values(map_zm_accounts_to_rows(accounts))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in AccountTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[AccountTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)


async def save_companies(connection: sa_async.AsyncConnection, companies: list[ZmCompany]) -> None:
    if not companies:
        return

    stmt = sa_postgresql.insert(CompanyTable).values(map_zm_companies_to_rows(companies))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in CompanyTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[CompanyTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)


async def save_countries(connection: sa_async.AsyncConnection, countries: list[ZmCountry]) -> None:
    if not countries:
        return

    stmt = sa_postgresql.insert(CountryTable).values(map_zm_countries_to_rows(countries))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in CountryTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[CountryTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)


async def save_instruments(connection: sa_async.AsyncConnection, instruments: list[ZmInstrument]) -> None:
    if not instruments:
        return

    stmt = sa_postgresql.insert(InstrumentTable).values(map_zm_instruments_to_rows(instruments))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in InstrumentTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[InstrumentTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)


async def save_merchants(connection: sa_async.AsyncConnection, merchants: list[ZmMerchant]) -> None:
    if not merchants:
        return

    stmt = sa_postgresql.insert(MerchantTable).values(map_zm_merchants_to_rows(merchants))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in MerchantTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[MerchantTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)


async def save_tags(connection: sa_async.AsyncConnection, tags: list[ZmTag]) -> None:
    if not tags:
        return

    stmt = sa_postgresql.insert(TagTable).values(map_zm_tags_to_rows(tags))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in TagTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[TagTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)


async def save_users(connection: sa_async.AsyncConnection, users: list[ZmUser]) -> None:
    if not users:
        return

    stmt = sa_postgresql.insert(UserTable).values(map_zm_users_to_rows(users))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in UserTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[UserTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)


async def save_transactions(connection: sa_async.AsyncConnection, transactions: list[ZmTransaction]) -> None:
    if not transactions or len(transactions) == 0:
        return

    stmt = sa_postgresql.insert(TransactionsTable).values(map_zm_transactions_to_rows(transactions))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in TransactionsTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[TransactionsTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)


def map_zm_accounts_to_rows(accounts: Iterable[ZmAccount]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for a in accounts:
        rows.append(
            {
                "id": a.id,
                "changed": a.changed,
                "user": a.user,
                "instrument": a.instrument,
                "title": a.title,
                "company": a.company,
                "type": a.type,
                "sync_id": a.sync_id or [],
                "balance": a.balance,
                "start_balance": a.start_balance,
                "credit_limit": a.credit_limit,
                "in_balance": a.in_balance,
                "savings": a.savings,
                "enable_correction": a.enable_correction,
                "enable_sms": a.enable_sms,
                "archive": a.archive,
                "private": a.private,
                "capitalization": a.capitalization,
                "percent": a.percent,
                "start_date": a.start_date,
                "end_date_offset": a.end_date_offset,
                "end_date_offset_interval": a.end_date_offset_interval,
                "payoff_step": a.payoff_step,
                "payoff_interval": a.payoff_interval,
                "balance_correction_type": a.balance_correction_type,
            }
        )
    return rows


def map_zm_companies_to_rows(companies: Iterable[ZmCompany]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for c in companies:
        rows.append(
            {
                "id": c.id,
                "changed": c.changed,
                "title": c.title,
                "full_title": c.full_title,
                "www": c.www,
                "country": c.country,
                "country_code": c.country_code,
                "deleted": c.deleted,
            }
        )
    return rows


def map_zm_countries_to_rows(countries: Iterable[ZmCountry]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for c in countries:
        rows.append(
            {
                "id": c.id,
                "title": c.title,
                "currency": c.currency,
                "domain": c.domain,
            }
        )
    return rows


def map_zm_instruments_to_rows(instruments: Iterable[ZmInstrument]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i in instruments:
        rows.append(
            {
                "id": i.id,
                "changed": i.changed,
                "title": i.title,
                "short_title": i.short_title,
                "symbol": i.symbol,
                "rate": i.rate,
            }
        )
    return rows


def map_zm_merchants_to_rows(merchants: Iterable[ZmMerchant]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for m in merchants:
        rows.append(
            {
                "id": m.id,
                "changed": m.changed,
                "user": m.user,
                "title": m.title,
            }
        )
    return rows


def map_zm_tags_to_rows(tags: Iterable[ZmTag]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for t in tags:
        rows.append(
            {
                "id": t.id,
                "changed": t.changed,
                "user": t.user,
                "title": t.title,
                "parent": t.parent,
                "icon": t.icon,
                "static_id": t.static_id,
                "picture": t.picture,
                "color": t.color,
                "show_income": t.show_income,
                "show_outcome": t.show_outcome,
                "budget_income": t.budget_income,
                "budget_outcome": t.budget_outcome,
                "required": t.required,
                "archive": t.archive,
            }
        )
    return rows


def map_zm_users_to_rows(users: Iterable[ZmUser]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for u in users:
        rows.append(
            {
                "id": u.id,
                "changed": u.changed,
                "currency": u.currency,
                "parent": u.parent,
                "country": u.country,
                "country_code": u.country_code,
                "email": u.email,
                "login": u.login,
                "month_start_day": u.month_start_day,
                "is_forecast_enabled": u.is_forecast_enabled,
                "plan_balance_mode": u.plan_balance_mode,
                "plan_settings": u.plan_settings,
                "paid_till": u.paid_till,
                "subscription": u.subscription,
                "subscription_renewal_date": u.subscription_renewal_date,
            }
        )
    return rows


def map_zm_transactions_to_rows(txns: Iterable[ZmTransaction]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for t in txns:
        rows.append(
            {
                "id": t.id,
                "user": t.user,
                "income": t.income,
                "outcome": t.outcome,
                "changed": t.changed,
                "income_instrument": t.income_instrument,
                "outcome_instrument": t.outcome_instrument,
                "created": t.created,
                "original_payee": t.original_payee,
                "deleted": t.deleted,
                "viewed": t.viewed,
                "hold": t.hold,
                "qr_code": t.qr_code,
                "source": t.source,
                "income_account": t.income_account,
                "outcome_account": t.outcome_account,
                "comment": t.comment,
                "payee": t.payee,
                "op_income": t.op_income,
                "op_outcome": t.op_outcome,
                "op_income_instrument": t.op_income_instrument,
                "op_outcome_instrument": t.op_outcome_instrument,
                "latitude": t.latitude,
                "longitude": t.longitude,
                "merchant": t.merchant,
                "income_bank": t.income_bank,
                "outcome_bank": t.outcome_bank,
                "reminder_marker": t.reminder_marker,
                "tags": t.tag or [],
                "date": t.date,
                "mcc": t.mcc,
            }
        )
    return rows
