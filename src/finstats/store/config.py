import os

from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import command
from finstats.container import Container
from finstats.store.accounts import AccountsRepository
from finstats.store.companies import CompaniesRepository
from finstats.store.connection import ConnectionScope
from finstats.store.countries import CountriesRepository
from finstats.store.instruments import InstrumentsRepository
from finstats.store.merchants import MerchantsRepository
from finstats.store.sqlalchemy_prometheus import instrument_engine
from finstats.store.tags import TagsRepository
from finstats.store.timestamp import TimestampRepository
from finstats.store.transactions import TransactionsRepository
from finstats.store.users import UsersRepository


def get_pg_url_from_env(use_psycopg: bool = False) -> str:
    dbname = os.environ.get("POSTGRES_DB", "finstats")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5431")
    user = os.environ.get("POSTGRES_USER", "test")
    password = os.environ.get("POSTGRES_PASSWORD", "test")
    if use_psycopg:
        return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}"
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"


def run_migrations(pg_url_sync: str) -> None:
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", pg_url_sync)
    command.upgrade(cfg, "head")


def configure_container(container: Container, pg_url: str) -> AsyncEngine:
    engine = create_async_engine(pg_url, pool_pre_ping=True)
    instrument_engine(engine, pool_name="finstats")

    container.register(ConnectionScope, instance=ConnectionScope(engine))
    container.register(AccountsRepository)
    container.register(CompaniesRepository)
    container.register(CountriesRepository)
    container.register(InstrumentsRepository)
    container.register(MerchantsRepository)
    container.register(TagsRepository)
    container.register(TimestampRepository)
    container.register(TransactionsRepository)
    container.register(UsersRepository)
    return engine
