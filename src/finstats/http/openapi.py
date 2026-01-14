from __future__ import annotations

import os

from aiohttp import web
from aiohttp_apigami import setup_aiohttp_apispec


def setup_openapi(app: web.Application) -> None:
    """Setup OpenAPI 3.0.3 documentation with Swagger UI"""

    servers: list[dict[str, str]] = []
    token = os.getenv("FLY_MACHINE_ID")
    if token is not None:
        servers = [{"url": "https://finstats.fly.dev"}]

    setup_aiohttp_apispec(
        app=app,
        title="finstats",
        version="v1",
        request_data_name="validated_data",
        swagger_path="/api/doc",
        url="/api/doc/openapi.json",
        openapi_version="3.0.3",
        servers=servers,
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
