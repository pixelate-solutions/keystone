from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Account, Anomaly, Obligation, Role, Scenario, Transaction
from app.schemas.dashboard import (
    HealthSignal,
    HealthSignalsResponse,
    RunwayDriver,
    TransactionCategorySummary,
    TransactionItem,
)
from app.services.forecasting import ForecastInputs, compute_runway


def _default_summary() -> str:
    return "Cash posture is steady. Review upcoming obligations to preserve optionality."


async def get_cash_position(session: AsyncSession, clerk_org_id: str) -> int:
    stmt = select(func.coalesce(func.sum(Account.current_balance_cents), 0)).where(
        Account.clerk_org_id == clerk_org_id,
        Account.currency_code == "USD",
    )
    result = await session.execute(stmt)
    return int(result.scalar_one() or 0)


async def get_upcoming_obligation_total(
    session: AsyncSession,
    clerk_org_id: str,
    from_date: date,
    to_date: date,
) -> int:
    stmt = select(func.coalesce(func.sum(Obligation.amount_cents), 0)).where(
        Obligation.clerk_org_id == clerk_org_id,
        Obligation.currency_code == "USD",
        Obligation.due_date >= from_date,
        Obligation.due_date <= to_date,
    )
    result = await session.execute(stmt)
    return int(result.scalar_one() or 0)


async def get_average_daily_net(session: AsyncSession, clerk_org_id: str, trailing_days: int = 30) -> int:
    start_date = date.today() - timedelta(days=trailing_days)
    stmt = select(func.coalesce(func.sum(Transaction.amount_cents), 0)).where(
        Transaction.clerk_org_id == clerk_org_id,
        Transaction.currency_code == "USD",
        Transaction.date >= start_date,
    )
    total = int((await session.execute(stmt)).scalar_one() or 0)
    return int(total / max(trailing_days, 1))


async def get_role_monthly_cost(session: AsyncSession, clerk_org_id: str, role_id: UUID | None) -> int:
    if not role_id:
        return 0
    role = await session.get(Role, role_id)
    if role and role.clerk_org_id == clerk_org_id:
        return int(role.monthly_cost_cents)
    return 0


async def get_scenario(session: AsyncSession, clerk_org_id: str, scenario_id: UUID | None) -> Scenario | None:
    if not scenario_id:
        return None
    scenario = await session.get(Scenario, scenario_id)
    if not scenario or scenario.clerk_org_id != clerk_org_id:
        return None
    return scenario


async def compute_runway_response(
    session: AsyncSession,
    clerk_org_id: str,
    days: int,
    scenario_id: UUID | None,
) -> tuple[int, int, list[RunwayDriver]]:
    cash = await get_cash_position(session, clerk_org_id)
    net_daily = await get_average_daily_net(session, clerk_org_id)
    obligations = await get_upcoming_obligation_total(
        session,
        clerk_org_id,
        date.today(),
        date.today() + timedelta(days=days),
    )

    scenario = await get_scenario(session, clerk_org_id, scenario_id)
    added_hire = await get_role_monthly_cost(
        session,
        clerk_org_id,
        scenario.add_hire_role_id if scenario else None,
    )

    runway_days, projected_end_cash, drivers = compute_runway(
        ForecastInputs(
            current_cash_cents=cash,
            average_daily_net_cents=net_daily,
            upcoming_obligations_cents=obligations,
            days=days,
            revenue_delta_pct=scenario.revenue_delta_pct if scenario else 0,
            added_hire_monthly_cents=added_hire,
        )
    )
    return runway_days, projected_end_cash, [RunwayDriver(**d) for d in drivers]


async def compute_health_signals(session: AsyncSession, clerk_org_id: str) -> HealthSignalsResponse:
    runway_days, _, _ = await compute_runway_response(session, clerk_org_id, days=90, scenario_id=None)

    anomalies_stmt = select(func.count(Anomaly.anomaly_id)).where(
        Anomaly.clerk_org_id == clerk_org_id,
        Anomaly.detected_at >= datetime.now(UTC) - timedelta(days=7),
    )
    anomaly_count = int((await session.execute(anomalies_stmt)).scalar_one() or 0)

    if runway_days >= 180:
        status = "stable"
    elif runway_days >= 90:
        status = "strained"
    else:
        status = "at_risk"

    signals = [
        HealthSignal(
            label=status,
            summary={
                "stable": "Stable runway posture",
                "strained": "Timing-sensitive runway posture",
                "at_risk": "Runway requires immediate timing control",
            }[status],
            reason=f"Current modeled runway is {runway_days} days.",
        )
    ]

    if anomaly_count:
        signals.append(
            HealthSignal(
                label="strained" if status == "stable" else status,
                summary="Recent anomalies detected",
                reason=f"{anomaly_count} anomaly signals in the last 7 days.",
            )
        )

    return HealthSignalsResponse(
        status=status,
        signals=signals,
        changed_since_last_week=_default_summary(),
    )


def obligations_window_query(clerk_org_id: str, from_date: date, to_date: date) -> Select[tuple[Obligation]]:
    return (
        select(Obligation)
        .where(
            Obligation.clerk_org_id == clerk_org_id,
            Obligation.due_date >= from_date,
            Obligation.due_date <= to_date,
        )
        .order_by(Obligation.due_date.asc())
    )


async def get_recent_transactions(
    session: AsyncSession,
    clerk_org_id: str,
    limit: int = 50,
) -> list[TransactionItem]:
    stmt = (
        select(Transaction)
        .where(
            Transaction.clerk_org_id == clerk_org_id,
            Transaction.currency_code == "USD",
        )
        .order_by(Transaction.date.desc())
        .limit(limit)
    )
    rows = (await session.execute(stmt)).scalars().all()
    return [
        TransactionItem(
            txn_id=str(row.txn_id),
            date=row.date,
            name=row.name,
            amount_cents=row.amount_cents,
            currency_code="USD",
            merchant=row.merchant,
            category=row.category,
            is_pending=row.is_pending,
        )
        for row in rows
    ]


async def get_category_summaries(
    session: AsyncSession,
    clerk_org_id: str,
    limit: int = 8,
) -> list[TransactionCategorySummary]:
    stmt = (
        select(
            func.coalesce(Transaction.category, "uncategorized").label("category"),
            func.coalesce(func.sum(Transaction.amount_cents), 0).label("total_cents"),
            func.count(Transaction.txn_id).label("transaction_count"),
        )
        .where(
            Transaction.clerk_org_id == clerk_org_id,
            Transaction.currency_code == "USD",
        )
        .group_by(func.coalesce(Transaction.category, "uncategorized"))
        .order_by(func.abs(func.coalesce(func.sum(Transaction.amount_cents), 0)).desc())
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()
    return [
        TransactionCategorySummary(
            category=row.category,
            total_cents=int(row.total_cents or 0),
            transaction_count=int(row.transaction_count or 0),
        )
        for row in rows
    ]
