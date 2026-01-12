import datetime
import decimal
import uuid

import sqlalchemy as sa
from alembic.config import Config
from sqlalchemy import orm
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from alembic import command
from finstats.store.config import get_pg_url_from_env


def run_migrations() -> None:
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", get_pg_url_from_env(use_psycopg=True))  # sync driver
    command.upgrade(cfg, "head")


def create_engine() -> AsyncEngine:
    url = get_pg_url_from_env(use_psycopg=False)
    return create_async_engine(url, pool_pre_ping=True)


class Base(DeclarativeBase):
    pass


METADATA = Base.metadata


class TimestampTable(Base):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    last_synced_timestamp: orm.Mapped[datetime.datetime] = orm.mapped_column(sa.DateTime(timezone=True))

    __tablename__ = "last_synced_timestamp"


class AccountTable(Base):
    id: orm.Mapped[uuid.UUID] = orm.mapped_column(sa.Uuid, primary_key=True)
    changed: orm.Mapped[datetime.datetime] = orm.mapped_column(sa.DateTime(timezone=True))
    user: orm.Mapped[int] = orm.mapped_column(sa.Integer)
    instrument: orm.Mapped[int | None] = orm.mapped_column(sa.Integer, nullable=True)
    title: orm.Mapped[str] = orm.mapped_column(sa.Text)
    role: orm.Mapped[int | None] = orm.mapped_column(sa.Integer, nullable=True)
    company: orm.Mapped[int | None] = orm.mapped_column(sa.Integer, nullable=True)
    type: orm.Mapped[str] = orm.mapped_column(sa.Text)
    sync_id: orm.Mapped[list[str]] = orm.mapped_column(sa.ARRAY(sa.Text), nullable=False, default=list)
    balance: orm.Mapped[decimal.Decimal] = orm.mapped_column(sa.DECIMAL)
    start_balance: orm.Mapped[decimal.Decimal] = orm.mapped_column(sa.DECIMAL)
    credit_limit: orm.Mapped[decimal.Decimal] = orm.mapped_column(sa.DECIMAL)
    in_balance: orm.Mapped[bool] = orm.mapped_column(sa.Boolean)
    savings: orm.Mapped[bool] = orm.mapped_column(sa.Boolean)
    enable_correction: orm.Mapped[bool] = orm.mapped_column(sa.Boolean)
    enable_sms: orm.Mapped[bool] = orm.mapped_column(sa.Boolean)
    archive: orm.Mapped[bool] = orm.mapped_column(sa.Boolean)
    private: orm.Mapped[bool] = orm.mapped_column(sa.Boolean)
    capitalization: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    percent: orm.Mapped[decimal.Decimal | None] = orm.mapped_column(sa.DECIMAL)
    start_date: orm.Mapped[datetime.datetime | None] = orm.mapped_column(sa.DateTime(timezone=True), nullable=True)
    end_date_offset: orm.Mapped[int | None] = orm.mapped_column(sa.Integer, nullable=True)
    end_date_offset_interval: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    payoff_step: orm.Mapped[int | None] = orm.mapped_column(sa.Integer, nullable=True)
    payoff_interval: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    balance_correction_type: orm.Mapped[str] = orm.mapped_column(sa.Text, nullable=False)

    __tablename__ = "account"


class UserTable(Base):
    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    changed: orm.Mapped[datetime.datetime] = orm.mapped_column(sa.DateTime(timezone=True))
    currency: orm.Mapped[int] = orm.mapped_column(sa.Integer)
    parent: orm.Mapped[int | None] = orm.mapped_column(sa.Integer, nullable=True)
    country: orm.Mapped[int] = orm.mapped_column(sa.Integer)
    country_code: orm.Mapped[str] = orm.mapped_column(sa.Text)
    email: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    login: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    month_start_day: orm.Mapped[int] = orm.mapped_column(sa.Integer)
    is_forecast_enabled: orm.Mapped[bool] = orm.mapped_column(sa.Boolean)
    plan_balance_mode: orm.Mapped[str] = orm.mapped_column(sa.Text)
    plan_settings: orm.Mapped[str] = orm.mapped_column(sa.Text)
    paid_till: orm.Mapped[datetime.datetime] = orm.mapped_column(sa.DateTime(timezone=True))
    subscription: orm.Mapped[str] = orm.mapped_column(sa.Text)
    subscription_renewal_date: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)

    __tablename__ = "user"


class TagTable(Base):
    id: orm.Mapped[uuid.UUID] = orm.mapped_column(sa.Uuid, primary_key=True)
    changed: orm.Mapped[datetime.datetime] = orm.mapped_column(sa.DateTime(timezone=True))
    user: orm.Mapped[int] = orm.mapped_column(sa.Integer)
    title: orm.Mapped[str] = orm.mapped_column(sa.Text)
    parent: orm.Mapped[uuid.UUID | None] = orm.mapped_column(sa.Uuid, nullable=True)
    icon: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    static_id: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    picture: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    color: orm.Mapped[int | None] = orm.mapped_column(sa.BigInteger, nullable=True)
    show_income: orm.Mapped[bool] = orm.mapped_column(sa.Boolean)
    show_outcome: orm.Mapped[bool] = orm.mapped_column(sa.Boolean)
    budget_income: orm.Mapped[bool] = orm.mapped_column(sa.Boolean)
    budget_outcome: orm.Mapped[bool] = orm.mapped_column(sa.Boolean)
    required: orm.Mapped[bool | None] = orm.mapped_column(sa.Boolean, nullable=True)
    archive: orm.Mapped[bool] = orm.mapped_column(sa.Boolean)

    __tablename__ = "tag"


class InstrumentTable(Base):
    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    changed: orm.Mapped[datetime.datetime] = orm.mapped_column(sa.DateTime(timezone=True))
    title: orm.Mapped[str] = orm.mapped_column(sa.Text)
    short_title: orm.Mapped[str] = orm.mapped_column(sa.Text)
    symbol: orm.Mapped[str] = orm.mapped_column(sa.Text)
    rate: orm.Mapped[decimal.Decimal] = orm.mapped_column(sa.DECIMAL)

    __tablename__ = "instrument"


class CountryTable(Base):
    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    title: orm.Mapped[str] = orm.mapped_column(sa.Text)
    currency: orm.Mapped[int] = orm.mapped_column(sa.Integer)
    domain: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)

    __tablename__ = "country"


class CompanyTable(Base):
    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    changed: orm.Mapped[datetime.datetime] = orm.mapped_column(sa.DateTime(timezone=True))
    title: orm.Mapped[str] = orm.mapped_column(sa.Text)
    full_title: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    www: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    country: orm.Mapped[int | None] = orm.mapped_column(sa.Integer, nullable=True)
    country_code: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    deleted: orm.Mapped[bool] = orm.mapped_column(sa.Boolean)

    __tablename__ = "company"


class MerchantTable(Base):
    id: orm.Mapped[uuid.UUID] = orm.mapped_column(sa.Uuid, primary_key=True)
    changed: orm.Mapped[datetime.datetime] = orm.mapped_column(sa.DateTime(timezone=True))
    user: orm.Mapped[int] = orm.mapped_column(sa.Integer)
    title: orm.Mapped[str] = orm.mapped_column(sa.Text)

    __tablename__ = "merchant"


class TransactionsTable(Base):
    id: orm.Mapped[uuid.UUID] = orm.mapped_column(sa.Uuid, primary_key=True)
    user: orm.Mapped[int] = orm.mapped_column(sa.Integer)
    income: orm.Mapped[decimal.Decimal] = orm.mapped_column(sa.DECIMAL)
    outcome: orm.Mapped[decimal.Decimal] = orm.mapped_column(sa.DECIMAL)
    changed: orm.Mapped[datetime.datetime] = orm.mapped_column(sa.DateTime(timezone=True))
    income_instrument: orm.Mapped[int] = orm.mapped_column(sa.Integer)
    outcome_instrument: orm.Mapped[int] = orm.mapped_column(sa.Integer)
    created: orm.Mapped[datetime.datetime] = orm.mapped_column(sa.DateTime(timezone=True))
    original_payee: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    deleted: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, server_default=sa.false())
    viewed: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, server_default=sa.false())
    hold: orm.Mapped[bool | None] = orm.mapped_column(sa.Boolean, nullable=True)
    qr_code: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    source: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    income_account: orm.Mapped[uuid.UUID] = orm.mapped_column(sa.Uuid)
    outcome_account: orm.Mapped[uuid.UUID] = orm.mapped_column(sa.Uuid)
    comment: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    payee: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    op_income: orm.Mapped[decimal.Decimal | None] = orm.mapped_column(sa.DECIMAL, nullable=True)
    op_outcome: orm.Mapped[decimal.Decimal | None] = orm.mapped_column(sa.DECIMAL, nullable=True)
    op_income_instrument: orm.Mapped[int | None] = orm.mapped_column(sa.Integer, nullable=True)
    op_outcome_instrument: orm.Mapped[int | None] = orm.mapped_column(sa.Integer, nullable=True)
    latitude: orm.Mapped[decimal.Decimal | None] = orm.mapped_column(sa.DECIMAL, nullable=True)
    longitude: orm.Mapped[decimal.Decimal | None] = orm.mapped_column(sa.DECIMAL, nullable=True)
    merchant: orm.Mapped[uuid.UUID | None] = orm.mapped_column(sa.Uuid, nullable=True)
    income_bank: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    outcome_bank: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    reminder_marker: orm.Mapped[uuid.UUID | None] = orm.mapped_column(sa.Uuid, nullable=True)
    mcc: orm.Mapped[int | None] = orm.mapped_column(sa.Integer, nullable=True)

    tags: orm.Mapped[list[uuid.UUID]] = orm.mapped_column(sa.ARRAY(sa.Uuid), nullable=False, default=list)
    date: orm.Mapped[datetime.date] = orm.mapped_column(sa.Date)

    __tablename__ = "transactions"
    __table_args__ = (
        sa.Index(
            "idx_transactions_exist_by_date_and_created", "date", "created", postgresql_where=sa.text("deleted = false")
        ),
    )
