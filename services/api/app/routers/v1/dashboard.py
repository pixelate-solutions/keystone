from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_context, get_db
from app.core.security import AuthContext
from app.schemas.dashboard import (
    CashPositionResponse,
    HealthSignalsResponse,
    ObligationsResponse,
    RunwayResponse,
    TransactionsResponse,
)
from app.schemas.common import ObligationOut
from app.services.dashboard import (
    compute_health_signals,
    compute_runway_response,
    get_category_summaries,
    get_cash_position,
    get_recent_transactions,
    obligations_window_query,
)

router = APIRouter()


@router.get("/cash-position", response_model=CashPositionResponse)
async def cash_position(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> CashPositionResponse:
    amount = await get_cash_position(session, context.clerk_org_id)
    return CashPositionResponse(amount_cents=amount, as_of=datetime.now(UTC))


@router.get("/runway", response_model=RunwayResponse)
async def runway(
    days: int = Query(default=30, ge=30, le=365),
    scenario_id: UUID | None = Query(default=None),
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> RunwayResponse:
    runway_days, projected_end_cash, drivers = await compute_runway_response(
        session=session,
        clerk_org_id=context.clerk_org_id,
        days=days,
        scenario_id=scenario_id,
    )
    return RunwayResponse(
        days_requested=days,
        runway_days=runway_days,
        projected_end_cash_cents=projected_end_cash,
        drivers=drivers,
    )


@router.get("/obligations", response_model=ObligationsResponse)
async def obligations(
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> ObligationsResponse:
    start = from_date or date.today()
    end = to_date or (start + timedelta(days=45))

    stmt = obligations_window_query(context.clerk_org_id, start, end)
    rows = (await session.execute(stmt)).scalars().all()

    return ObligationsResponse(
        items=[
            ObligationOut(
                obligation_id=row.obligation_id,
                type=row.type,
                name=row.name,
                amount_cents=row.amount_cents,
                currency_code=row.currency_code,
                due_date=row.due_date,
                cadence=row.cadence,
                notes=row.notes,
            )
            for row in rows
        ]
    )


@router.get("/health-signals", response_model=HealthSignalsResponse)
async def health_signals(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> HealthSignalsResponse:
    return await compute_health_signals(session, context.clerk_org_id)


@router.get("/transactions", response_model=TransactionsResponse)
async def transactions(
    limit: int = Query(default=50, ge=1, le=200),
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> TransactionsResponse:
    items = await get_recent_transactions(session, context.clerk_org_id, limit=limit)
    categories = await get_category_summaries(session, context.clerk_org_id, limit=8)
    return TransactionsResponse(items=items, categories=categories)
