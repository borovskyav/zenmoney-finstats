from __future__ import annotations

from typing import Any

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
