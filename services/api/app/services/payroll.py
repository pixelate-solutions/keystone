from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import PayrollPlan, Role


async def payroll_summary(session: AsyncSession, clerk_org_id: str) -> dict:
    plan_stmt = select(PayrollPlan).where(PayrollPlan.clerk_org_id == clerk_org_id)
    plan = (await session.execute(plan_stmt)).scalar_one_or_none()

    baseline = int(plan.baseline_monthly_cents if plan else 0)
    multiplier = float(plan.fully_loaded_multiplier if plan else 1.2)

    role_stmt = select(func.coalesce(func.sum(Role.monthly_cost_cents), 0)).where(
        Role.clerk_org_id == clerk_org_id,
        Role.is_planned.is_(True),
    )
    planned_hires = int((await session.execute(role_stmt)).scalar_one() or 0)

    estimated_revenue = max(1, int((baseline + planned_hires) * 3.5))
    payroll_pct = ((baseline + planned_hires) / estimated_revenue) * 100

    can_hire_until = date.today() + timedelta(days=120 if payroll_pct < 35 else 45)

    return {
        "baseline_monthly_cents": baseline,
        "fully_loaded_multiplier": multiplier,
        "planned_hires_monthly_cents": int(planned_hires * multiplier),
        "payroll_pct_of_revenue": round(payroll_pct, 2),
        "can_hire_until": can_hire_until,
    }
