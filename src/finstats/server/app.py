from __future__ import annotations

from aiohttp import web

from finstats.args import CliArgs
from finstats.server.accounts import AccountsController
from finstats.server.health import HealthController
from finstats.server.instruments import InstrumentsController
from finstats.server.merchants import MerchantsController
from finstats.server.middleware import auth_mw, error_middleware, request_id_middleware
from finstats.server.openapi import setup_openapi
from finstats.server.tags import TagsController
from finstats.server.transaction_expense import ExpenseTransactionsController
from finstats.server.transaction_income import IncomeTransactionsController
from finstats.server.transactions import TransactionsController


def register_service_routes(app: web.Application) -> None:
    app.router.add_view("/health", HealthController)


def create_web_server(app: web.Application, args: CliArgs) -> None:
    setup_openapi(app, args)

    web_server = web.Application(middlewares=[error_middleware, request_id_middleware, auth_mw])
    web_server.router.add_view("/v1/transactions", TransactionsController)
    web_server.router.add_view("/v1/transactions/expenses", ExpenseTransactionsController)
    web_server.router.add_view("/v1/transactions/incomes", IncomeTransactionsController)
    web_server.router.add_view("/v1/accounts", AccountsController)
    web_server.router.add_view("/v1/tags", TagsController)
    web_server.router.add_view("/v1/instruments", InstrumentsController)
    web_server.router.add_view("/v1/merchants", MerchantsController)

    app.add_subapp("/api", web_server)
