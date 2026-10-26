from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import AuthContext, verifier
from app.db.session import get_async_session

security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_session():
        yield session


async def get_current_context(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthContext:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    context = await verifier.verify(credentials.credentials)
    request.state.clerk_user_id = context.clerk_user_id
    request.state.clerk_org_id = context.clerk_org_id
    return context
