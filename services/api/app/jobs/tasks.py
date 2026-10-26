from __future__ import annotations

import asyncio
from dataclasses import dataclass

from redis import Redis
from rq import Retry
from rq.exceptions import InvalidJobOperation
from rq.job import Job

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.jobs.queue import get_queue, get_redis
from app.services.plaid import sync_connection_data


@dataclass
class SyncJobPayload:
    clerk_org_id: str
    connection_id: str
    days_back: int


def plaid_sync_job_id(payload: SyncJobPayload) -> str:
    return f"plaid_sync:{payload.clerk_org_id}:{payload.connection_id}:{payload.days_back}"


def enqueue_plaid_sync(payload: SyncJobPayload) -> tuple[str, str]:
    queue = get_queue("plaid")
    job_id = plaid_sync_job_id(payload)

    existing = queue.fetch_job(job_id)
    if existing and existing.get_status(refresh=False) in {"queued", "started", "deferred"}:
        return job_id, "already_syncing"

    job = queue.enqueue(
        run_plaid_sync,
        payload.clerk_org_id,
        payload.connection_id,
        payload.days_back,
        job_id=job_id,
        retry=Retry(max=3, interval=[30, 120, 300]),
    )
    return job.id, "queued"


async def _run_sync_async(clerk_org_id: str, connection_id: str, days_back: int) -> None:
    async with AsyncSessionLocal() as session:
        await sync_connection_data(
            session=session,
            clerk_org_id=clerk_org_id,
            connection_id=connection_id,
            days_back=days_back,
        )


def run_plaid_sync(clerk_org_id: str, connection_id: str, days_back: int) -> None:
    asyncio.run(_run_sync_async(clerk_org_id, connection_id, days_back))


def is_connection_syncing(connection_id: str) -> bool:
    redis: Redis = get_redis()
    pattern = f"rq:job:plaid_sync:*:{connection_id}:*"
    keys = redis.keys(pattern)
    for key in keys:
        job_id = key.decode().replace("rq:job:", "")
        try:
            job = Job.fetch(job_id, connection=redis)
            if job.get_status(refresh=False) in {"queued", "started", "deferred"}:
                return True
        except (InvalidJobOperation, Exception):
            continue
    return False
