from pydantic import BaseModel


class PlaidLinkTokenRequest(BaseModel):
    client_name: str = "Keystone"


class PlaidLinkTokenResponse(BaseModel):
    link_token: str


class PlaidExchangeRequest(BaseModel):
    public_token: str
    institution_name: str | None = None


class PlaidExchangeResponse(BaseModel):
    connection_id: str
    status: str


class PlaidSyncRequest(BaseModel):
    connection_id: str
    days_back: int | None = None
