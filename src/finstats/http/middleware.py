from __future__ import annotations

import logging
import time
import time as time_module
import uuid
from collections.abc import Awaitable, Callable

from aiohttp import web
from aiohttp.web_request import Request

from finstats.contracts import ZenMoneyClientAuthException
from finstats.http.context import get_client, get_token

Handler = Callable[[Request], Awaitable[web.StreamResponse]]

log = logging.getLogger("finstats.http")


def _get_request_id(request: Request) -> str:
    # если пришёл request-id от клиента/прокси — уважаем, иначе генерим
    rid = request.headers.get("X-Request-ID") or request.headers.get("X-Request-Id")
    return rid if rid else uuid.uuid4().hex


def _get_peer(request: Request) -> str:
    # request.remote иногда None, делаем безопасно
    peer = request.remote
    if peer:
        return peer
    transport = request.transport
    if transport is None:
        return "-"
    info = transport.get_extra_info("peername")
    if not info:
        return "-"
    return str(info[0])


@web.middleware
async def auth_mw(request: Request, handler: Handler) -> web.StreamResponse:
    token = get_token(request)

    client = get_client(request)
    try:
        await client.fetch_diff(token, int(time_module.time()), 2)
    except ZenMoneyClientAuthException as e:
        log.info("ZenMoney auth failed: %r", e)
        raise web.HTTPUnauthorized(reason="Invalid Authorization token") from None

    return await handler(request)


@web.middleware
async def request_id_middleware(request: Request, handler: Handler) -> web.StreamResponse:
    request_id = _get_request_id(request)
    request["request_id"] = request_id

    try:
        resp = await handler(request)
    except web.HTTPException as e:
        e.headers["X-Request-ID"] = request_id
        raise
    else:
        resp.headers["X-Request-ID"] = request_id
        return resp


@web.middleware
async def access_log_middleware(request: Request, handler: Handler) -> web.StreamResponse:
    start = time.perf_counter()
    request_id = request.get("request_id")

    try:
        resp = await handler(request)
    except web.HTTPException as e:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        log.info(
            "%s %s -> %s in %.1fms rid=%s peer=%s ua=%r",
            request.method,
            request.path_qs,
            e.status,
            elapsed_ms,
            request_id,
            _get_peer(request),
            request.headers.get("User-Agent", "-"),
        )
        raise
    except Exception:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        log.exception(
            "%s %s -> 500 in %.1fms rid=%s peer=%s ua=%r",
            request.method,
            request.path_qs,
            elapsed_ms,
            request_id,
            _get_peer(request),
            request.headers.get("User-Agent", "-"),
        )
        raise
    else:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        log.info(
            "%s %s -> %s in %.1fms rid=%s peer=%s",
            request.method,
            request.path_qs,
            resp.status,
            elapsed_ms,
            request_id,
            _get_peer(request),
        )
        return resp
