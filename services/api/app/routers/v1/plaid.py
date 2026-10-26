from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_context, get_db
from app.core.security import AuthContext
from app.jobs.tasks import SyncJobPayload, enqueue_plaid_sync, is_connection_syncing
from app.models.models import Connection
from app.schemas.common import ConnectionOut
from app.schemas.plaid import (
    PlaidExchangeRequest,
    PlaidExchangeResponse,
    PlaidLinkTokenResponse,
    PlaidSyncRequest,
)
from app.services.plaid import create_link_token, exchange_public_token

router = APIRouter()


@router.post("/link-token", response_model=PlaidLinkTokenResponse)
async def link_token(context: AuthContext = Depends(get_current_context)) -> PlaidLinkTokenResponse:
    token = await create_link_token(context.clerk_user_id, context.clerk_org_id)
    return PlaidLinkTokenResponse(link_token=token)


@router.post("/exchange", response_model=PlaidExchangeResponse)
async def exchange(
    payload: PlaidExchangeRequest,
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> PlaidExchangeResponse:
    if not settings.plaid_client_id or not settings.plaid_secret:
        raise HTTPException(status_code=500, detail="Plaid not configured")

    connection = await exchange_public_token(
        session,
        context.clerk_org_id,
        payload.public_token,
        payload.institution_name,
    )

    await session.refresh(connection)
    return PlaidExchangeResponse(connection_id=str(connection.connection_id), status=connection.status)


@router.post("/sync")
async def sync_connection(
    payload: PlaidSyncRequest,
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    stmt = select(Connection).where(
        Connection.connection_id == payload.connection_id,
        Connection.clerk_org_id == context.clerk_org_id,
    )
    connection = (await session.execute(stmt)).scalar_one_or_none()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    if is_connection_syncing(payload.connection_id):
        return {"job_status": "already_syncing", "connection_status": connection.status}

    days_back = payload.days_back or settings.plaid_sync_days
    job_id, job_status = enqueue_plaid_sync(
        SyncJobPayload(
            clerk_org_id=context.clerk_org_id,
            connection_id=str(connection.connection_id),
            days_back=days_back,
        )
    )

    connection.status = "syncing"
    connection.last_error = None
    await session.commit()

    return {"job_id": job_id, "job_status": job_status, "connection_status": connection.status}


@router.get("/connections", response_model=list[ConnectionOut])
async def connections(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> list[ConnectionOut]:
    stmt = select(Connection).where(Connection.clerk_org_id == context.clerk_org_id)
    items = (await session.execute(stmt)).scalars().all()
    return [
        ConnectionOut(
            connection_id=item.connection_id,
            institution=item.institution,
            status=item.status,
            last_error=item.last_error,
            last_sync_at=item.last_sync_at,
        )
        for item in items
    ]
