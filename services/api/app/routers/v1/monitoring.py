from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_context, get_db
from app.core.security import AuthContext
from app.models.models import Anomaly, Transaction
from app.schemas.common import AnomalyOut
from app.services.anomalies import (
    TransactionSignal,
    detect_duplicate_payments,
    detect_spend_spikes,
    detect_subscription_creep,
)

router = APIRouter()


@router.get("/anomalies", response_model=list[AnomalyOut])
async def anomalies(
    limit: int = Query(default=20, ge=1, le=100),
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_db),
) -> list[AnomalyOut]:
    existing_stmt = (
        select(Anomaly)
        .where(Anomaly.clerk_org_id == context.clerk_org_id)
        .order_by(Anomaly.detected_at.desc())
        .limit(limit)
    )
    existing = (await session.execute(existing_stmt)).scalars().all()
    if existing:
        return [
            AnomalyOut(
                anomaly_id=a.anomaly_id,
                type=a.type,
                severity=a.severity,
                confidence=a.confidence,
                title=a.title,
                explanation=a.explanation,
                detected_at=a.detected_at,
                related_txn_ids=a.related_txn_ids or [],
            )
            for a in existing
        ]

    tx_stmt = select(Transaction).where(
        Transaction.clerk_org_id == context.clerk_org_id,
        Transaction.date >= date.today() - timedelta(days=90),
    )
    txns = (await session.execute(tx_stmt)).scalars().all()

    signals = [
        TransactionSignal(
            txn_id=str(txn.txn_id),
            date=txn.date,
            merchant=txn.merchant or txn.name,
            category=txn.category or "uncategorized",
            amount_cents=txn.amount_cents,
        )
        for txn in txns
    ]

    detected = detect_spend_spikes(signals) + detect_duplicate_payments(signals) + detect_subscription_creep(signals)

    results: list[AnomalyOut] = []
    for finding in detected[:limit]:
        row = Anomaly(clerk_org_id=context.clerk_org_id, **finding)
        session.add(row)
        await session.flush()
        results.append(
            AnomalyOut(
                anomaly_id=row.anomaly_id,
                type=row.type,
                severity=row.severity,
                confidence=row.confidence,
                title=row.title,
                explanation=row.explanation,
                detected_at=row.detected_at,
                related_txn_ids=row.related_txn_ids or [],
            )
        )

    await session.commit()
    return results
