from __future__ import annotations

from collections.abc import Iterator
from typing import Any, TypeAliasType

from aiohttp import web
from aiohttp_apigami import setup_aiohttp_apispec

from finstats.args import CliArgs

OPENAI_EXT: dict[str, Any] = {"x-openai-isConsequential": True}


def setup_openapi(app: web.Application, args: CliArgs) -> None:
    setup_aiohttp_apispec(
        app=app,
        title="finstats",
        version=args.hosting_environment.version(),
        request_data_name="validated_data",
        swagger_path="/doc",
        url="/doc/openapi.json",
        openapi_version="3.0.3",
        servers=[{"url": args.hosting_environment.server()}],
        components={
            "securitySchemes": {
                "BearerAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "Authorization",
                    "description": "API token (paste your token directly, not 'Bearer <token>')",
                }
            }
        },
    )

    app.on_startup.append(_patch_openapi_for_actions)


# dirty hack for strEnum values that should be annotated as a string type in openapi schema
async def _patch_openapi_for_actions(app: web.Application) -> None:
    swagger = app.get("swagger_dict")
    if not isinstance(swagger, dict):
        return

    # Patch parameters schemas
    for node in _walk(swagger.get("paths", {})):
        params = node.get("parameters")
        if not isinstance(params, list):
            continue
        for prm in params:
            if not isinstance(prm, dict):
                continue
            schema = prm.get("schema")
            if isinstance(schema, dict):
                _normalize_openapi_schema(schema)

    # Patch component schemas too (optional, but keeps spec consistent)
    for node in _walk(swagger.get("components", {})):
        if isinstance(node, dict) and "schema" in node and isinstance(node["schema"], dict):
            _normalize_openapi_schema(node["schema"])

    # Also walk all schemas under components/schemas recursively
    for node in _walk(swagger.get("components", {}).get("schemas", {})):
        if isinstance(node, dict) and ("enum" in node or "nullable" in node):
            _normalize_openapi_schema(node)


def _walk(obj: TypeAliasType) -> Iterator[dict[str, Any]]:
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)


def _normalize_openapi_schema(schema: dict) -> None:
    # 1) enum without type -> assume string (safe default for params)
    if "enum" in schema and "type" not in schema:
        schema["type"] = "string"

    # 2) remove nullable + None-in-enum (Actions hate this combo)
    if "enum" in schema:
        enum = schema["enum"]
        if isinstance(enum, list):
            schema["enum"] = [v for v in enum if v is not None]
        schema.pop("nullable", None)
