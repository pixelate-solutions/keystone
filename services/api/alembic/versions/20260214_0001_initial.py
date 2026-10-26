"""initial schema

Revision ID: 20260214_0001
Revises:
Create Date: 2026-02-14 00:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260214_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("clerk_org_id", sa.String(length=255), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_user_id", sa.String(length=255), nullable=False),
        sa.Column("clerk_org_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_clerk_org_id", "users", ["clerk_org_id"])

    op.create_table(
        "connections",
        sa.Column("connection_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_org_id", sa.String(length=255), nullable=False),
        sa.Column("plaid_item_id", sa.String(length=255), nullable=False, unique=True),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("institution", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_connections_clerk_org_id", "connections", ["clerk_org_id"])

    op.create_table(
        "accounts",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_org_id", sa.String(length=255), nullable=False),
        sa.Column(
            "connection_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("connections.connection_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("plaid_account_id", sa.String(length=255), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("subtype", sa.String(length=100), nullable=True),
        sa.Column("mask", sa.String(length=10), nullable=True),
        sa.Column("currency_code", sa.String(length=10), nullable=False, server_default="USD"),
        sa.Column("current_balance_cents", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("available_balance_cents", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_accounts_clerk_org_id", "accounts", ["clerk_org_id"])

    op.create_table(
        "transactions",
        sa.Column("txn_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_org_id", sa.String(length=255), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.account_id"), nullable=False),
        sa.Column("plaid_transaction_id", sa.String(length=255), nullable=True, unique=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("amount_cents", sa.BigInteger(), nullable=False),
        sa.Column("currency_code", sa.String(length=10), nullable=False, server_default="USD"),
        sa.Column("merchant", sa.String(length=255), nullable=True),
        sa.Column("category", sa.String(length=255), nullable=True),
        sa.Column("is_pending", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("raw_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_transactions_clerk_org_id", "transactions", ["clerk_org_id"])
    op.create_index("idx_transactions_org_date", "transactions", ["clerk_org_id", "date"])

    op.create_table(
        "obligations",
        sa.Column("obligation_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_org_id", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("amount_cents", sa.BigInteger(), nullable=False),
        sa.Column("currency_code", sa.String(length=10), nullable=False, server_default="USD"),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("cadence", sa.String(length=64), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_obligations_clerk_org_id", "obligations", ["clerk_org_id"])
    op.create_index("idx_obligations_org_due", "obligations", ["clerk_org_id", "due_date"])

    op.create_table(
        "payroll_plans",
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_org_id", sa.String(length=255), nullable=False, unique=True),
        sa.Column("baseline_monthly_cents", sa.BigInteger(), nullable=False),
        sa.Column("fully_loaded_multiplier", sa.Float(), nullable=False),
        sa.Column("currency_code", sa.String(length=10), nullable=False, server_default="USD"),
    )
    op.create_index("ix_payroll_plans_clerk_org_id", "payroll_plans", ["clerk_org_id"])

    op.create_table(
        "roles",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_org_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("monthly_cost_cents", sa.BigInteger(), nullable=False),
        sa.Column("currency_code", sa.String(length=10), nullable=False, server_default="USD"),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("is_planned", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_roles_clerk_org_id", "roles", ["clerk_org_id"])

    op.create_table(
        "scenarios",
        sa.Column("scenario_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_org_id", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("revenue_delta_pct", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("vendor_terms_shift_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("add_hire_role_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_scenarios_clerk_org_id", "scenarios", ["clerk_org_id"])

    op.create_table(
        "anomalies",
        sa.Column("anomaly_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_org_id", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("confidence", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("related_txn_ids", sa.JSON(), nullable=True),
    )
    op.create_index("ix_anomalies_clerk_org_id", "anomalies", ["clerk_org_id"])
    op.create_index("idx_anomalies_org_detected", "anomalies", ["clerk_org_id", "detected_at"])

    op.create_table(
        "billing_customers",
        sa.Column("billing_customer_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_org_id", sa.String(length=255), nullable=False, unique=True),
        sa.Column("stripe_customer_id", sa.String(length=255), nullable=False, unique=True),
    )
    op.create_index("ix_billing_customers_clerk_org_id", "billing_customers", ["clerk_org_id"])

    op.create_table(
        "subscriptions",
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_org_id", sa.String(length=255), nullable=False, unique=True),
        sa.Column("stripe_subscription_id", sa.String(length=255), nullable=False, unique=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("price_id", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_subscriptions_clerk_org_id", "subscriptions", ["clerk_org_id"])


def downgrade() -> None:
    op.drop_index("ix_subscriptions_clerk_org_id", table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_index("ix_billing_customers_clerk_org_id", table_name="billing_customers")
    op.drop_table("billing_customers")

    op.drop_index("idx_anomalies_org_detected", table_name="anomalies")
    op.drop_index("ix_anomalies_clerk_org_id", table_name="anomalies")
    op.drop_table("anomalies")

    op.drop_index("ix_scenarios_clerk_org_id", table_name="scenarios")
    op.drop_table("scenarios")

    op.drop_index("ix_roles_clerk_org_id", table_name="roles")
    op.drop_table("roles")

    op.drop_index("ix_payroll_plans_clerk_org_id", table_name="payroll_plans")
    op.drop_table("payroll_plans")

    op.drop_index("idx_obligations_org_due", table_name="obligations")
    op.drop_index("ix_obligations_clerk_org_id", table_name="obligations")
    op.drop_table("obligations")

    op.drop_index("idx_transactions_org_date", table_name="transactions")
    op.drop_index("ix_transactions_clerk_org_id", table_name="transactions")
    op.drop_table("transactions")

    op.drop_index("ix_accounts_clerk_org_id", table_name="accounts")
    op.drop_table("accounts")

    op.drop_index("ix_connections_clerk_org_id", table_name="connections")
    op.drop_table("connections")

    op.drop_index("ix_users_clerk_org_id", table_name="users")
    op.drop_table("users")

    op.drop_table("organizations")
