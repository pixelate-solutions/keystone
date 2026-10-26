from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_context, get_db
from app.core.security import AuthContext
from app.models.models import Scenario
from app.schemas.dashboard import ScenarioCreateRequest, ScenarioOut

router = APIRouter()


@router.post("/scenarios", response_model=ScenarioOut)
async def create_scenario(
    payload: ScenarioCreateRequest,
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> ScenarioOut:
    scenario = Scenario(
        clerk_org_id=context.clerk_org_id,
        name=payload.name,
        revenue_delta_pct=payload.revenue_delta_pct,
        vendor_terms_shift_days=payload.vendor_terms_shift_days,
        add_hire_role_id=payload.add_hire_role_id,
    )
    session.add(scenario)
    await session.commit()
    await session.refresh(scenario)
    return ScenarioOut(
        scenario_id=str(scenario.scenario_id),
        name=scenario.name,
        revenue_delta_pct=scenario.revenue_delta_pct,
        vendor_terms_shift_days=scenario.vendor_terms_shift_days,
        add_hire_role_id=str(scenario.add_hire_role_id) if scenario.add_hire_role_id else None,
        created_at=scenario.created_at,
    )


@router.get("/scenarios", response_model=list[ScenarioOut])
async def list_scenarios(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> list[ScenarioOut]:
    stmt = (
        select(Scenario)
        .where(Scenario.clerk_org_id == context.clerk_org_id)
        .order_by(Scenario.created_at.desc())
    )
    rows = (await session.execute(stmt)).scalars().all()
    return [
        ScenarioOut(
            scenario_id=str(row.scenario_id),
            name=row.name,
            revenue_delta_pct=row.revenue_delta_pct,
            vendor_terms_shift_days=row.vendor_terms_shift_days,
            add_hire_role_id=str(row.add_hire_role_id) if row.add_hire_role_id else None,
            created_at=row.created_at,
        )
        for row in rows
    ]
