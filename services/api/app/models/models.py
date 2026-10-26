from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import BIGINT, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Organization(Base):
    __tablename__ = "organizations"

    clerk_org_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    clerk_org_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class Connection(Base):
    __tablename__ = "connections"

    connection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_org_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    plaid_item_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    institution: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    accounts: Mapped[list[Account]] = relationship(back_populates="connection")


class Account(Base):
    __tablename__ = "accounts"

    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_org_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    connection_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("connections.connection_id", ondelete="SET NULL"),
        nullable=True,
    )
    plaid_account_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    subtype: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mask: Mapped[str | None] = mapped_column(String(10), nullable=True)
    currency_code: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    current_balance_cents: Mapped[int] = mapped_column(BIGINT, default=0, nullable=False)
    available_balance_cents: Mapped[int | None] = mapped_column(BIGINT, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    connection: Mapped[Connection | None] = relationship(back_populates="accounts")
    transactions: Mapped[list[Transaction]] = relationship(back_populates="account")


class Transaction(Base):
    __tablename__ = "transactions"

    txn_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_org_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.account_id"))
    plaid_transaction_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount_cents: Mapped[int] = mapped_column(BIGINT, nullable=False)
    currency_code: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    merchant: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_pending: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    account: Mapped[Account] = relationship(back_populates="transactions")


class Obligation(Base):
    __tablename__ = "obligations"

    obligation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_org_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount_cents: Mapped[int] = mapped_column(BIGINT, nullable=False)
    currency_code: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    cadence: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class PayrollPlan(Base):
    __tablename__ = "payroll_plans"

    plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_org_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True, unique=True)
    baseline_monthly_cents: Mapped[int] = mapped_column(BIGINT, nullable=False)
    fully_loaded_multiplier: Mapped[float] = mapped_column(Float, default=1.2, nullable=False)
    currency_code: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)


class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_org_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    monthly_cost_cents: Mapped[int] = mapped_column(BIGINT, nullable=False)
    currency_code: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_planned: Mapped[bool] = mapped_column(Boolean, default=True)


class Scenario(Base):
    __tablename__ = "scenarios"

    scenario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_org_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    revenue_delta_pct: Mapped[int] = mapped_column(nullable=False, default=0)
    vendor_terms_shift_days: Mapped[int] = mapped_column(nullable=False, default=0)
    add_hire_role_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class Anomaly(Base):
    __tablename__ = "anomalies"

    anomaly_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_org_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    related_txn_ids: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)


class BillingCustomer(Base):
    __tablename__ = "billing_customers"

    billing_customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    clerk_org_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    stripe_customer_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)


class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_org_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    stripe_subscription_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    price_id: Mapped[str | None] = mapped_column(String(255), nullable=True)


Index("idx_transactions_org_date", Transaction.clerk_org_id, Transaction.date)
Index("idx_obligations_org_due", Obligation.clerk_org_id, Obligation.due_date)
Index("idx_anomalies_org_detected", Anomaly.clerk_org_id, Anomaly.detected_at)
