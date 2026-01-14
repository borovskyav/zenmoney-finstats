from __future__ import annotations

import dataclasses
from typing import Annotated

import aiohttp_apigami
import marshmallow_recipe as mr
from aiohttp import web

from finstats.contracts import TagId, ZmTag
from finstats.http.context import ErrorResponse, get_engine
from finstats.store.tags import get_children_tags, get_tags


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class GetTagsResponse:
    tags: Annotated[list[TagModel], mr.meta(description="List of tag objects")]


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class TagModel(ZmTag):
    children: Annotated[list[TagId], mr.meta(description="List of children tags")]


class TagsController(web.View):
    @aiohttp_apigami.docs(security=[{"BearerAuth": []}])
    @aiohttp_apigami.docs(tags=["Tags"], summary="Get tags", operationId="tagsList")
    @aiohttp_apigami.response_schema(mr.schema(GetTagsResponse), 200)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 401)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 500)
    async def get(self) -> web.StreamResponse:
        engine = get_engine(self.request)

        tag_models: list[TagModel] = []

        async with engine.begin() as conn:
            tags = await get_tags(connection=conn)
            for tag in tags:
                children = await get_children_tags(connection=conn, parent_tag_id=tag.id)
                tag_model = TagModel(**dataclasses.asdict(tag), children=[child.id for child in children])
                tag_models.append(tag_model)

        response = GetTagsResponse(tag_models)
        return web.json_response(mr.dump(response))
