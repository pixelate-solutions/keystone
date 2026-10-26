from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_context, get_db
from app.core.security import AuthContext
from app.models.models import Role
from app.schemas.dashboard import PayrollSummaryResponse, RoleCreateRequest, RoleOut
from app.services.payroll import payroll_summary

router = APIRouter()


@router.get("/summary", response_model=PayrollSummaryResponse)
async def summary(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> PayrollSummaryResponse:
    data = await payroll_summary(session, context.clerk_org_id)
    return PayrollSummaryResponse(**data)


@router.post("/roles", response_model=RoleOut)
async def add_role(
    payload: RoleCreateRequest,
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> RoleOut:
    role = Role(
        clerk_org_id=context.clerk_org_id,
        title=payload.title,
        monthly_cost_cents=payload.monthly_cost_cents,
        start_date=payload.start_date,
        is_planned=payload.is_planned,
        currency_code="USD",
    )
    session.add(role)
    await session.commit()
    await session.refresh(role)
    return RoleOut(
        role_id=str(role.role_id),
        title=role.title,
        monthly_cost_cents=role.monthly_cost_cents,
        start_date=role.start_date,
        is_planned=role.is_planned,
    )


@router.get("/roles", response_model=list[RoleOut])
async def list_roles(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> list[RoleOut]:
    stmt = select(Role).where(Role.clerk_org_id == context.clerk_org_id).order_by(Role.start_date.asc())
    rows = (await session.execute(stmt)).scalars().all()
    return [
        RoleOut(
            role_id=str(row.role_id),
            title=row.title,
            monthly_cost_cents=row.monthly_cost_cents,
            start_date=row.start_date,
            is_planned=row.is_planned,
        )
        for row in rows
    ]
