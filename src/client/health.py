import dataclasses
from typing import Annotated

import marshmallow_recipe as mr


@dataclasses.dataclass(frozen=True, slots=True)
class HealthResponse:
    api: Annotated[str, mr.meta(description="API service status")]
    last_synced_timestamp: Annotated[str, mr.meta(description="Unix timestamp of the last successful data synchronization")]
