import dataclasses
import datetime
import decimal
from typing import Annotated

import marshmallow_recipe as mr

from client.models import InstrumentId


@dataclasses.dataclass(frozen=True, slots=True)
class GetInstrumentsResponse:
    instruments: Annotated[list[InstrumentModel], mr.meta(description="List of instrument objects")]


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class InstrumentModel:
    id: Annotated[InstrumentId, mr.meta(description="Unique identifier of the instrument")]
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Last modification timestamp")]
    title: Annotated[str, mr.meta(description="Instrument title")]
    short_title: Annotated[str, mr.meta(description="Short instrument title")]
    symbol: Annotated[str, mr.meta(description="Instrument symbol")]
    rate: Annotated[decimal.Decimal, mr.meta(description="Exchange rate relative to the base instrument")]
