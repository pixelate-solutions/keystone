from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_context, get_db
from app.core.security import AuthContext
from app.models.models import Anomaly, Obligation
from app.schemas.guidance import GuidanceQuestionsResponse, GuidanceSummaryResponse
from app.services.dashboard import compute_health_signals, compute_runway_response
from app.services.guidance import GuidanceSnapshot, get_guidance_provider

router = APIRouter()
provider = get_guidance_provider()


@router.get("/summary", response_model=GuidanceSummaryResponse)
async def summary(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> GuidanceSummaryResponse:
    runway_days, _, _ = await compute_runway_response(session, context.clerk_org_id, days=90, scenario_id=None)
    health = await compute_health_signals(session, context.clerk_org_id)

    anomaly_count = int(
        (await session.execute(select(func.count(Anomaly.anomaly_id)).where(Anomaly.clerk_org_id == context.clerk_org_id))).scalar_one()
        or 0
    )
    obligation_count = int(
        (
            await session.execute(
                select(func.count(Obligation.obligation_id)).where(Obligation.clerk_org_id == context.clerk_org_id)
            )
        ).scalar_one()
        or 0
    )

    summary_text, drivers = await provider.summary(
        GuidanceSnapshot(
            health_status=health.status,
            runway_days=runway_days,
            anomalies_count=anomaly_count,
            obligation_pressure=obligation_count > 5,
        )
    )
    return GuidanceSummaryResponse(summary=summary_text, key_drivers=drivers)


@router.get("/questions", response_model=GuidanceQuestionsResponse)
async def questions(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> GuidanceQuestionsResponse:
    runway_days, _, _ = await compute_runway_response(session, context.clerk_org_id, days=90, scenario_id=None)
    health = await compute_health_signals(session, context.clerk_org_id)
    anomaly_count = int(
        (await session.execute(select(func.count(Anomaly.anomaly_id)).where(Anomaly.clerk_org_id == context.clerk_org_id))).scalar_one()
        or 0
    )

    prompt_list = await provider.questions(
        GuidanceSnapshot(
            health_status=health.status,
            runway_days=runway_days,
            anomalies_count=anomaly_count,
            obligation_pressure=False,
        )
    )
    return GuidanceQuestionsResponse(questions=prompt_list)
