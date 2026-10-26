from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import AsyncSessionLocal
from app.jobs.queue import get_redis

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready() -> dict[str, str]:
    async with AsyncSessionLocal() as session:
        await session.execute(text("select 1"))

    redis = get_redis()
    redis.ping()

    return {"status": "ready"}
