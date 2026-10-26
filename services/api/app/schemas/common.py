from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


CurrencyCode = Literal["USD"]
HealthLabel = Literal["stable", "strained", "at_risk"]
ConnectionStatus = Literal["pending", "syncing", "ready", "error"]


class MessageResponse(BaseModel):
    message: str


class ConnectionOut(BaseModel):
    connection_id: UUID
    institution: str | None
    status: ConnectionStatus
    last_error: str | None = None
    last_sync_at: datetime | None = None


class ObligationOut(BaseModel):
    obligation_id: UUID
    type: Literal["payroll", "vendor", "debt"]
    name: str
    amount_cents: int
    currency_code: CurrencyCode = "USD"
    due_date: date
    cadence: str | None = None
    notes: str | None = None


class AnomalyOut(BaseModel):
    anomaly_id: UUID
    type: str
    severity: Literal["low", "medium", "high"]
    confidence: Literal["low", "medium", "high"]
    title: str
    explanation: str
    detected_at: datetime
    related_txn_ids: list[str] = Field(default_factory=list)
