from __future__ import annotations

import dataclasses
import uuid
from typing import Annotated

import marshmallow_recipe as mr

InstrumentId = int
UserId = int
CountryId = int
TagId = uuid.UUID
CompanyId = int
AccountId = uuid.UUID
MerchantId = uuid.UUID
TransactionId = uuid.UUID
ReminderMarkerId = uuid.UUID


@dataclasses.dataclass(frozen=True, slots=True)
class ErrorResponse:
    message: Annotated[str, mr.meta(description="Error message describing what went wrong")]
