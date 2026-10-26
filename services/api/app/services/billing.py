from __future__ import annotations

from datetime import UTC, datetime

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.models import BillingCustomer, Subscription

stripe.api_key = settings.stripe_secret_key


async def get_or_create_customer(session: AsyncSession, clerk_org_id: str) -> BillingCustomer:
    stmt = select(BillingCustomer).where(BillingCustomer.clerk_org_id == clerk_org_id)
    existing = (await session.execute(stmt)).scalar_one_or_none()
    if existing:
        return existing

    created = stripe.Customer.create(metadata={"clerk_org_id": clerk_org_id})
    customer = BillingCustomer(clerk_org_id=clerk_org_id, stripe_customer_id=created["id"])
    session.add(customer)
    await session.commit()
    await session.refresh(customer)
    return customer


async def create_checkout_session(
    session: AsyncSession,
    clerk_org_id: str,
    success_url: str,
    cancel_url: str,
) -> str:
    customer = await get_or_create_customer(session, clerk_org_id)
    checkout = stripe.checkout.Session.create(
        customer=customer.stripe_customer_id,
        mode="subscription",
        line_items=[{"price": settings.stripe_pro_price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        allow_promotion_codes=True,
    )
    return str(checkout.url)


async def create_portal_session(session: AsyncSession, clerk_org_id: str, return_url: str) -> str:
    customer = await get_or_create_customer(session, clerk_org_id)
    portal = stripe.billing_portal.Session.create(customer=customer.stripe_customer_id, return_url=return_url)
    return str(portal.url)


async def billing_status(session: AsyncSession, clerk_org_id: str) -> dict:
    stmt = select(Subscription).where(Subscription.clerk_org_id == clerk_org_id)
    subscription = (await session.execute(stmt)).scalar_one_or_none()

    if not subscription:
        return {
            "tier": "free",
            "subscription_status": "inactive",
            "current_period_end": None,
            "portal_available": False,
        }

    tier = "pro" if subscription.status in {"active", "trialing", "past_due"} else "free"
    return {
        "tier": tier,
        "subscription_status": subscription.status,
        "current_period_end": subscription.current_period_end,
        "portal_available": True,
    }


async def upsert_subscription_from_event(session: AsyncSession, event: dict) -> None:
    event_type = event.get("type")

    if event_type == "checkout.session.completed":
        data = event["data"]["object"]
        customer_id = data.get("customer")
        subscription_id = data.get("subscription")

        customer_stmt = select(BillingCustomer).where(BillingCustomer.stripe_customer_id == customer_id)
        customer = (await session.execute(customer_stmt)).scalar_one_or_none()
        if not customer:
            return

        existing_stmt = select(Subscription).where(Subscription.clerk_org_id == customer.clerk_org_id)
        existing = (await session.execute(existing_stmt)).scalar_one_or_none()

        if existing:
            existing.stripe_subscription_id = subscription_id
            existing.status = "active"
        else:
            session.add(
                Subscription(
                    clerk_org_id=customer.clerk_org_id,
                    stripe_subscription_id=subscription_id,
                    status="active",
                )
            )

    if event_type in {"customer.subscription.updated", "customer.subscription.deleted"}:
        data = event["data"]["object"]
        customer_id = data.get("customer")

        customer_stmt = select(BillingCustomer).where(BillingCustomer.stripe_customer_id == customer_id)
        customer = (await session.execute(customer_stmt)).scalar_one_or_none()
        if not customer:
            return

        stmt = select(Subscription).where(Subscription.clerk_org_id == customer.clerk_org_id)
        subscription = (await session.execute(stmt)).scalar_one_or_none()

        period_end = data.get("current_period_end")
        period_end_dt = datetime.fromtimestamp(period_end, tz=UTC) if period_end else None

        if subscription:
            subscription.status = data.get("status", subscription.status)
            subscription.current_period_end = period_end_dt
            subscription.price_id = (
                data.get("items", {}).get("data", [{}])[0].get("price", {}).get("id")
            )
            subscription.stripe_subscription_id = data.get("id", subscription.stripe_subscription_id)
        else:
            session.add(
                Subscription(
                    clerk_org_id=customer.clerk_org_id,
                    stripe_subscription_id=data.get("id", ""),
                    status=data.get("status", "inactive"),
                    current_period_end=period_end_dt,
                    price_id=data.get("items", {}).get("data", [{}])[0].get("price", {}).get("id"),
                )
            )

    await session.commit()
