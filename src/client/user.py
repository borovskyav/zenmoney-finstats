import dataclasses
import datetime
from typing import Annotated

import marshmallow_recipe as mr

from client.models import CountryId, InstrumentId, UserId


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class UserModel:
    id: Annotated[UserId, mr.meta(description="Unique identifier of the user")]
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Last modification timestamp")]
    currency: Annotated[InstrumentId, mr.meta(description="Default currency/instrument ID for the user")]
    parent: Annotated[UserId | None, mr.meta(description="Parent user ID, if any")]
    country: Annotated[CountryId | None, mr.meta(description="Country ID of the user")]
    country_code: Annotated[str, mr.meta(description="Country code (ISO 3166-1 alpha-2)")]
    email: Annotated[str | None, mr.meta(description="User's email address")]
    login: Annotated[str | None, mr.meta(description="User's login name")]
    month_start_day: Annotated[int, mr.meta(description="Day of month when financial month starts")]
    is_forecast_enabled: Annotated[bool, mr.meta(description="Whether forecasting is enabled for the user")]
    plan_balance_mode: Annotated[str, mr.meta(description="Plan balance calculation mode")]
    plan_settings: Annotated[str, mr.meta(description="JSON-encoded plan settings")]
    paid_till: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Subscription paid until timestamp")]
    subscription: Annotated[str | None, mr.meta(description="Subscription type")]
    subscription_renewal_date: Annotated[str | None, mr.meta(description="Subscription renewal date")]
