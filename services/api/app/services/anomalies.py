from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class TransactionSignal:
    txn_id: str
    date: date
    merchant: str
    category: str
    amount_cents: int


def detect_spend_spikes(transactions: list[TransactionSignal], lookback_days: int = 30) -> list[dict]:
    if not transactions:
        return []

    latest_date = max(t.date for t in transactions)
    recent_cutoff = latest_date - timedelta(days=7)
    baseline_cutoff = latest_date - timedelta(days=lookback_days)

    recent_totals = defaultdict(int)
    baseline_totals = defaultdict(int)

    for txn in transactions:
        key = txn.category or txn.merchant or "uncategorized"
        if txn.date >= recent_cutoff:
            recent_totals[key] += max(txn.amount_cents, 0)
        elif txn.date >= baseline_cutoff:
            baseline_totals[key] += max(txn.amount_cents, 0)

    findings = []
    for key, recent in recent_totals.items():
        baseline_weekly = int(baseline_totals.get(key, 0) / max(1, lookback_days / 7))
        if baseline_weekly > 0 and recent > baseline_weekly * 2:
            findings.append(
                {
                    "type": "spend_spike",
                    "severity": "medium",
                    "confidence": "high",
                    "title": f"Spend spike in {key}",
                    "explanation": f"Last 7 days spend is {round(recent / baseline_weekly, 1)}x trailing average.",
                    "related_txn_ids": [],
                }
            )
    return findings


def detect_duplicate_payments(transactions: list[TransactionSignal]) -> list[dict]:
    findings = []
    seen: dict[tuple[str, int], TransactionSignal] = {}

    for txn in sorted(transactions, key=lambda t: t.date):
        if txn.amount_cents <= 0:
            continue
        key = (txn.merchant.lower(), txn.amount_cents)
        previous = seen.get(key)
        if previous and abs((txn.date - previous.date).days) <= 3:
            findings.append(
                {
                    "type": "duplicate_payment",
                    "severity": "high",
                    "confidence": "medium",
                    "title": f"Possible duplicate payment to {txn.merchant}",
                    "explanation": "Similar amount posted within 3 days.",
                    "related_txn_ids": [previous.txn_id, txn.txn_id],
                }
            )
        else:
            seen[key] = txn
    return findings


def detect_subscription_creep(transactions: list[TransactionSignal]) -> list[dict]:
    by_merchant: dict[str, list[TransactionSignal]] = defaultdict(list)
    for txn in transactions:
        if txn.amount_cents > 0 and txn.merchant:
            by_merchant[txn.merchant.lower()].append(txn)

    findings = []
    for merchant, items in by_merchant.items():
        if len(items) < 3:
            continue
        items.sort(key=lambda t: t.date)
        recent = items[-1].amount_cents
        previous = items[-2].amount_cents
        older = items[-3].amount_cents
        if previous > 0 and older > 0 and recent > previous >= older and recent >= int(older * 1.2):
            findings.append(
                {
                    "type": "subscription_creep",
                    "severity": "low",
                    "confidence": "medium",
                    "title": f"Subscription creep for {merchant.title()}",
                    "explanation": "Recurring charge has trended upward across recent cycles.",
                    "related_txn_ids": [str(items[-3].txn_id), str(items[-2].txn_id), str(items[-1].txn_id)],
                }
            )
    return findings
