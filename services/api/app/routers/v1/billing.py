from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_context, get_db
from app.core.security import AuthContext
from app.schemas.billing import BillingStatusResponse, CheckoutSessionResponse, PortalSessionResponse
from app.services.billing import billing_status, create_checkout_session, create_portal_session

router = APIRouter()


@router.post("/checkout-session", response_model=CheckoutSessionResponse)
async def checkout(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> CheckoutSessionResponse:
    if not settings.stripe_secret_key or not settings.stripe_pro_price_id:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    url = await create_checkout_session(
        session,
        context.clerk_org_id,
        success_url="http://localhost:3000/app/billing/success",
        cancel_url="http://localhost:3000/app/billing/cancel",
    )
    return CheckoutSessionResponse(url=url)


@router.post("/portal-session", response_model=PortalSessionResponse)
async def portal(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> PortalSessionResponse:
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    url = await create_portal_session(session, context.clerk_org_id, return_url="http://localhost:3000/app/settings")
    return PortalSessionResponse(url=url)


@router.get("/status", response_model=BillingStatusResponse)
async def status(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> BillingStatusResponse:
    data = await billing_status(session, context.clerk_org_id)
    return BillingStatusResponse(**data)
