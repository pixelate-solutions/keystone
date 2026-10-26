import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_db
from app.services.billing import upsert_subscription_from_event

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(request: Request, session: AsyncSession = Depends(get_db)) -> dict[str, str]:
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid payload") from exc
    except stripe.error.SignatureVerificationError as exc:
        raise HTTPException(status_code=400, detail="Invalid signature") from exc

    await upsert_subscription_from_event(session, event)
    return {"received": "true"}
