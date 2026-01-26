import dataclasses
import datetime
import enum
from typing import Annotated

import marshmallow_recipe as mr

from client.models import TagId, UserId


class TagType(enum.StrEnum):
    Income = "Income"
    Expense = "Expense"
    Both = "Both"


@dataclasses.dataclass(frozen=True, slots=True)
class GetTagsResponse:
    tags: Annotated[list[TagModel], mr.meta(description="List of tag objects")]


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class TagModel:
    id: Annotated[TagId, mr.meta(description="Unique identifier of the tag")]
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Last modification timestamp")]
    user: Annotated[UserId, mr.meta(description="ID of the user who owns this tag")]
    title: Annotated[str, mr.meta(description="Tag title")]
    parent: Annotated[TagId | None, mr.meta(description="Parent tag ID, if any")]
    icon: Annotated[str | None, mr.meta(description="Icon identifier for the tag")]
    static_id: Annotated[str | None, mr.meta(description="Static tag identifier from the source system")]
    picture: Annotated[str | None, mr.meta(description="Picture identifier or URL for the tag")]
    color: Annotated[int | None, mr.meta(description="Tag color as an integer value")]
    show_income: Annotated[bool, mr.meta(description="Whether the tag is shown for income transactions")]
    show_outcome: Annotated[bool, mr.meta(description="Whether the tag is shown for outcome transactions")]
    budget_income: Annotated[bool, mr.meta(description="Whether the tag is included in income budgets")]
    budget_outcome: Annotated[bool, mr.meta(description="Whether the tag is included in outcome budgets")]
    required: Annotated[bool | None, mr.meta(description="Whether the tag is required to classify transactions")]
    archive: Annotated[bool, mr.meta(description="Whether the tag is archived")]
    children: Annotated[list[TagId], mr.meta(description="List of children tag IDs")]
