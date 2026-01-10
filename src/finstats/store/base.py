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
    merchant: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    income_bank_id: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    outcome_bank_id: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)
    reminder_marker: orm.Mapped[uuid.UUID | None] = orm.mapped_column(sa.Uuid, nullable=True)

    tags: orm.Mapped[list[uuid.UUID]] = orm.mapped_column(sa.ARRAY(sa.Uuid), nullable=False, default=list)
    date: orm.Mapped[datetime.date] = orm.mapped_column(sa.Date)

    __tablename__ = "transactions"
    __table_args__ = (
        sa.Index("idx_transactions_exist_by_created", "created", postgresql_where=sa.text("deleted = false")),
    )
