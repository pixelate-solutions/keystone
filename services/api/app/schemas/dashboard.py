from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel

from app.schemas.common import HealthLabel, ObligationOut


class CashPositionResponse(BaseModel):
    amount_cents: int
    currency_code: Literal["USD"] = "USD"
    as_of: datetime


class RunwayDriver(BaseModel):
    label: str
    impact_cents: int
    detail: str


class RunwayResponse(BaseModel):
    days_requested: int
    runway_days: int
    projected_end_cash_cents: int
    currency_code: Literal["USD"] = "USD"
    drivers: list[RunwayDriver]


class ObligationsResponse(BaseModel):
    items: list[ObligationOut]


class TransactionItem(BaseModel):
    txn_id: str
    date: date
    name: str
    amount_cents: int
    currency_code: Literal["USD"] = "USD"
    merchant: str | None = None
    category: str | None = None
    is_pending: bool = False


class TransactionCategorySummary(BaseModel):
    category: str
    total_cents: int
    transaction_count: int


class TransactionsResponse(BaseModel):
    items: list[TransactionItem]
    categories: list[TransactionCategorySummary]


class HealthSignal(BaseModel):
    label: HealthLabel
    summary: str
    reason: str


class HealthSignalsResponse(BaseModel):
    status: HealthLabel
    signals: list[HealthSignal]
    changed_since_last_week: str


class ScenarioCreateRequest(BaseModel):
    name: str
    revenue_delta_pct: int = 0
    vendor_terms_shift_days: int = 0
    add_hire_role_id: str | None = None


class ScenarioOut(BaseModel):
    scenario_id: str
    name: str
    revenue_delta_pct: int
    vendor_terms_shift_days: int
    add_hire_role_id: str | None = None
    created_at: datetime


class PayrollSummaryResponse(BaseModel):
    baseline_monthly_cents: int
    fully_loaded_multiplier: float
    planned_hires_monthly_cents: int
    payroll_pct_of_revenue: float
    can_hire_until: date | None


class RoleCreateRequest(BaseModel):
    title: str
    monthly_cost_cents: int
    start_date: date | None = None
    is_planned: bool = True


class RoleOut(BaseModel):
    role_id: str
    title: str
    monthly_cost_cents: int
    start_date: date | None
    is_planned: bool
