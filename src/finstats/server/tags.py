from __future__ import annotations

import dataclasses
from typing import Annotated

import aiohttp_apigami
import marshmallow_recipe as mr
from aiohttp import web

from finstats.server.base import BaseController, ErrorResponse
from finstats.server.convert import tag_to_tag_model
from finstats.server.models import TagModel


@dataclasses.dataclass(frozen=True, slots=True)
class GetTagsResponse:
    tags: Annotated[list[TagModel], mr.meta(description="List of tag objects")]


class TagsController(BaseController):
    @aiohttp_apigami.docs(security=[{"BearerAuth": []}])
    @aiohttp_apigami.docs(tags=["Tags"], summary="Get tags", operationId="tagsList")
    @aiohttp_apigami.response_schema(mr.schema(GetTagsResponse), 200)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 401)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 500)
    async def get(self) -> web.StreamResponse:
        repository = self.get_tags_repository()
        tag_models: list[TagModel] = []
        tags = await repository.get_tags()
        for tag in tags:
            children = await repository.get_children_tags(parent_tag_id=tag.id)
            tag_model = tag_to_tag_model(tag, children_ids=[child.id for child in children])
            tag_models.append(tag_model)

        response = GetTagsResponse(tag_models)
        return web.json_response(mr.dump(response))
