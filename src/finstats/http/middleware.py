from __future__ import annotations

import asyncio
import logging
import time
import time as time_module
import uuid
from collections.abc import Awaitable, Callable

import marshmallow_recipe as mr
from aiohttp import web
from aiohttp.web_request import Request

from finstats.contracts import ZenMoneyClientAuthException
from finstats.http.context import ErrorResponse, get_client, get_token

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


@web.middleware
async def error_middleware(request: Request, handler: Handler) -> web.StreamResponse:
    try:
        return await handler(request)

    except web.HTTPException as e:
        if e.content_type == "application/json" and e.text:
            raise

        resp = web.json_response(mr.dump(ErrorResponse(e.reason or e.__class__.__name__)), status=e.status)
        resp.headers.update(e.headers)
        resp.set_status(e.status, reason=e.reason)
        return resp

    except asyncio.CancelledError:
        raise

    except Exception:
        log.exception("Unhandled error rid=%s path=%s", _get_request_id(request), request.path_qs)
        return web.json_response(mr.dump(ErrorResponse("Internal Server Error")), status=500)
