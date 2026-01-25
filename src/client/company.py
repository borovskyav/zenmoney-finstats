from __future__ import annotations

import dataclasses
import datetime
from typing import Annotated

import marshmallow_recipe as mr

from client.models import CompanyId, CountryId


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class CompanyModel:
    id: Annotated[CompanyId, mr.meta(description="Unique identifier of the company")]
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Last modification timestamp")]
    title: Annotated[str, mr.meta(description="Company name")]
    full_title: Annotated[str | None, mr.meta(description="Full company name")]
    www: Annotated[str | None, mr.meta(description="Company website URL")]
    country: Annotated[CountryId | None, mr.meta(description="Country ID of the company")]
    country_code: Annotated[str | None, mr.meta(description="Country code (ISO 3166-1 alpha-2)")]
    deleted: Annotated[bool, mr.meta(description="Whether the company is deleted")]
