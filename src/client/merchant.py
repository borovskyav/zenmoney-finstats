import dataclasses
import datetime
from typing import Annotated

import marshmallow_recipe as mr

from client.models import MerchantId, UserId


@dataclasses.dataclass(frozen=True, slots=True)
class GetMerchantsResponse:
    merchants: Annotated[list[MerchantModel], mr.meta(description="List of merchant objects")]


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class MerchantModel:
    id: Annotated[MerchantId, mr.meta(description="Unique identifier of the merchant")]
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Last modification timestamp")]
    user: Annotated[UserId, mr.meta(description="ID of the user who owns this merchant")]
    title: Annotated[str, mr.meta(description="Name of the merchant")]
