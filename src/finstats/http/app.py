from __future__ import annotations

from aiohttp import web

from finstats.http.accounts import AccountsController
from finstats.http.instruments import InstrumentsController
from finstats.http.merchants import MerchantsController
from finstats.http.middleware import auth_mw, error_middleware, request_id_middleware
from finstats.http.openapi import setup_openapi
from finstats.http.tags import TagsController
from finstats.http.transaction_expense import ExpenseTransactionsController
from finstats.http.transactions import TransactionsController


def serve_http(app: web.Application, host: str = "0.0.0.0", port: int = 8080) -> None:
    web.run_app(app, host=host, port=port, handle_signals=True)


def create_web_server(app: web.Application) -> None:
    setup_openapi(app)

    web_server = web.Application(middlewares=[error_middleware, request_id_middleware, auth_mw])
    web_server.router.add_view("/v1/transactions", TransactionsController)
    web_server.router.add_view("/v1/transactions/expenses", ExpenseTransactionsController)
    web_server.router.add_view("/v1/accounts", AccountsController)
    web_server.router.add_view("/v1/tags", TagsController)
    web_server.router.add_view("/v1/instruments", InstrumentsController)
    web_server.router.add_view("/v1/merchants", MerchantsController)

    app.add_subapp("/api", web_server)
