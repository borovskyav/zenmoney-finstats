import datetime
import enum

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.domain import AccountId, TagId, Transaction, TransactionId
from finstats.store.base import AccountTable, TagTable, TransactionsTable
from finstats.store.connection import ConnectionScope
from finstats.store.misc import from_dataclasses, to_dataclass, to_dataclasses


class TransactionTypeFilter(enum.StrEnum):
    Income = "Income"
    Expense = "Expense"
    Transfer = "Transfer"
    DebtRepaid = "DebtRepaid"
    LentOut = "LentOut"
    ReturnIncome = "ReturnIncome"
    ReturnExpense = "ReturnExpense"


class TransactionsRepository:
    __connection_scope: ConnectionScope

    def __init__(self, connection: ConnectionScope) -> None:
        self.__connection_scope = connection

    async def get_transaction(self, transaction_id: TransactionId) -> Transaction | None:
        stmt = sa.select(TransactionsTable).where(TransactionsTable.id == transaction_id)
        async with self.__connection_scope.acquire() as connection:
            result = await connection.execute(stmt)
            return to_dataclass(Transaction, result.one_or_none())

    async def find_transactions(
        self,
        offset: int = 0,
        limit: int = 100,
        from_date: datetime.date | None = None,
        to_date: datetime.date | None = None,
        not_viewed: bool = False,
        account_id: AccountId | None = None,
        tags: list[TagId] | None = None,
        transaction_type: TransactionTypeFilter | None = None,
    ) -> tuple[list[Transaction], int]:
        if from_date is not None and to_date is not None and from_date > to_date:
            raise ValueError(f"from_date {from_date} > to_date {to_date}")

        where_clause = TransactionsTable.deleted.is_(False)
        if from_date:
            where_clause &= TransactionsTable.date >= from_date

        if to_date:
            where_clause &= TransactionsTable.date <= to_date

        if not_viewed:
            where_clause &= TransactionsTable.viewed.is_(False)

        if account_id:
            where_clause &= (TransactionsTable.income_account == account_id) | (TransactionsTable.outcome_account == account_id)

        if tags:
            where_clause &= TransactionsTable.tags.op("&&")(tags)

        if transaction_type:
            type_expr = self._get_binary_expression_transaction_type(transaction_type)
            if type_expr is not None:
                where_clause &= type_expr

        stmt_count = sa.select(sa.func.count()).select_from(TransactionsTable).where(where_clause)
        stmt = (
            sa.select(TransactionsTable)
            .order_by(TransactionsTable.date.desc(), TransactionsTable.created.desc(), TransactionsTable.id.desc())
            .offset(offset)
            .limit(limit)
            .where(where_clause)
        )

        async with self.__connection_scope.acquire() as connection:
            total = (await connection.execute(stmt_count)).scalar_one()
            result = await connection.execute(stmt)
            return to_dataclasses(Transaction, result.all()), total

    async def save_transactions(self, transactions: list[Transaction]) -> None:
        if not transactions:
            return

        stmt = sa_postgresql.insert(TransactionsTable).values(from_dataclasses(transactions))
        excluded = stmt.excluded
        set_cols = {c.name: getattr(excluded, c.name) for c in TransactionsTable.__table__.columns if c.name != "id"}

        async with self.__connection_scope.acquire() as connection:
            stmt = stmt.on_conflict_do_update(
                index_elements=[TransactionsTable.id],
                set_=set_cols,
            )
            await connection.execute(stmt)

    @staticmethod
    def _get_binary_expression_transaction_type(
        transaction_type: TransactionTypeFilter,
    ) -> sa.ColumnElement[bool] | None:
        t = TransactionsTable

        income_tx = (t.outcome == 0) & (t.income > 0)
        expense_tx = (t.income == 0) & (t.outcome > 0)
        transfer_tx = (t.income > 0) & (t.outcome > 0)

        # первый тег или NULL
        has_tag = sa.func.cardinality(t.tags) > 0
        first_tag_id = sa.case((has_tag, t.tags[1]), else_=sa.null())

        # tag_type == Income / Expense (строго как _calculate_tag_type)
        tag_is_income = sa.exists(
            sa.select(1).where(
                TagTable.id == first_tag_id,
                TagTable.show_income.is_(True),
                TagTable.show_outcome.is_(False),
            )
        )
        tag_is_expense = sa.exists(
            sa.select(1).where(
                TagTable.id == first_tag_id,
                TagTable.show_outcome.is_(True),
                TagTable.show_income.is_(False),
            )
        )

        # tag_type is None:
        #  - тега нет
        #  - или есть тег, но show_income=false и show_outcome=false
        tag_is_none = ~has_tag | sa.exists(
            sa.select(1).where(
                TagTable.id == first_tag_id,
                TagTable.show_income.is_(False),
                TagTable.show_outcome.is_(False),
            )
        )
        tag_is_both_type = sa.exists(
            sa.select(1).where(
                TagTable.id == first_tag_id,
                TagTable.show_income.is_(True),
                TagTable.show_outcome.is_(True),
            )
        )

        income_acc_type = sa.select(AccountTable.type).where(AccountTable.id == t.income_account).scalar_subquery()
        outcome_acc_type = sa.select(AccountTable.type).where(AccountTable.id == t.outcome_account).scalar_subquery()

        match transaction_type:
            case TransactionTypeFilter.Income:
                return income_tx & (tag_is_income | tag_is_none | tag_is_both_type)

            case TransactionTypeFilter.ReturnIncome:
                return income_tx & tag_is_expense

            case TransactionTypeFilter.Expense:
                return expense_tx & (tag_is_expense | tag_is_none | tag_is_both_type)

            case TransactionTypeFilter.ReturnExpense:
                return expense_tx & tag_is_income

            case TransactionTypeFilter.LentOut:
                return transfer_tx & (income_acc_type == "debt")

            case TransactionTypeFilter.DebtRepaid:
                return transfer_tx & (outcome_acc_type == "debt")

            case TransactionTypeFilter.Transfer:
                return transfer_tx & (income_acc_type != "debt") & (outcome_acc_type != "debt")

        return None
