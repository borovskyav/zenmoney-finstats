import dataclasses
from typing import Annotated

import marshmallow_recipe as mr

from client.models import CountryId, InstrumentId


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class CountryModel:
    id: Annotated[CountryId, mr.meta(description="Unique identifier of the country")]
    title: Annotated[str, mr.meta(description="Country name")]
    currency: Annotated[InstrumentId, mr.meta(description="Default currency/instrument ID for the country")]
    domain: Annotated[str | None, mr.meta(description="Country domain")]
