from datetime import datetime

from pydantic import BaseModel, HttpUrl


class CheckoutSessionResponse(BaseModel):
    url: HttpUrl


class PortalSessionResponse(BaseModel):
    url: HttpUrl


class BillingStatusResponse(BaseModel):
    tier: str
    subscription_status: str
    current_period_end: datetime | None = None
    portal_available: bool
