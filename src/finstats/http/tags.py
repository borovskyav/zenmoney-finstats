from __future__ import annotations

import dataclasses
from typing import Annotated

import aiohttp_apigami
import marshmallow_recipe as mr
from aiohttp import web

from finstats.contracts import TagId, ZmTag
from finstats.http.context import ErrorResponse, get_engine
from finstats.store.tags import get_children_tags, get_tag, get_tags


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class GetTagsResponse:
    tags: Annotated[list[ZmTag], mr.meta(description="List of tag objects")]


class TagsController(web.View):
    @aiohttp_apigami.docs(security=[{"BearerAuth": []}])
    @aiohttp_apigami.docs(tags=["Tags"], summary="Get tags", operationId="tagsList")
    @aiohttp_apigami.response_schema(mr.schema(GetTagsResponse), 200)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 401)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 500)
    async def get(self) -> web.StreamResponse:
        engine = get_engine(self.request)

        async with engine.begin() as conn:
            tags = await get_tags(connection=conn)

        response = GetTagsResponse(tags)
        return web.json_response(mr.dump(response))


@dataclasses.dataclass(frozen=True, slots=True)
class GetTagChildrenMatchData:
    tag_id: Annotated[TagId, mr.meta(description="Parent tag ID to list children for")]


class TagChildrenController(web.View):
    @aiohttp_apigami.docs(security=[{"BearerAuth": []}])
    @aiohttp_apigami.docs(tags=["Tags"], summary="Get all children of tag", operationId="tagChildren")
    @aiohttp_apigami.match_info_schema(mr.schema(GetTagChildrenMatchData))
    @aiohttp_apigami.response_schema(mr.schema(GetTagsResponse), 200)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), code=400, description="Match data or query is not valid")
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 401)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), code=404, description="Tag not found")
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 500)
    async def get(self) -> web.StreamResponse:
        match_info = self.parse_and_validate_match_info(self.request)

        engine = get_engine(self.request)
        async with engine.begin() as conn:
            tag = await get_tag(connection=conn, tag_id=match_info.tag_id)
            if tag is None:
                raise web.HTTPNotFound(reason="tag by given tag_id is not found")
            tags = await get_children_tags(connection=conn, parent_tag_id=match_info.tag_id)

        response = GetTagsResponse(tags)
        return web.json_response(mr.dump(response))

    @staticmethod
    def parse_and_validate_match_info(request: web.Request) -> GetTagChildrenMatchData:
        try:
            match_info = mr.load(GetTagChildrenMatchData, dict(request.match_info))
        except mr.ValidationError as e:
            raise web.HTTPBadRequest(reason=f"failed to parse match info: {e.normalized_messages()}") from None

        return match_info
