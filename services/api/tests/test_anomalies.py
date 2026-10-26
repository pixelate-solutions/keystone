from datetime import date, timedelta

from app.services.anomalies import (
    TransactionSignal,
    detect_duplicate_payments,
    detect_spend_spikes,
    detect_subscription_creep,
)


def test_detect_duplicate_payments() -> None:
    today = date.today()
    transactions = [
        TransactionSignal("1", today - timedelta(days=2), "Vendor A", "Ops", 25_000),
        TransactionSignal("2", today, "Vendor A", "Ops", 25_000),
    ]

    findings = detect_duplicate_payments(transactions)
    assert len(findings) == 1
    assert findings[0]["type"] == "duplicate_payment"


def test_detect_spend_spikes() -> None:
    today = date.today()
    transactions = [
        TransactionSignal("1", today - timedelta(days=25), "Cloud", "Infra", 10_000),
        TransactionSignal("2", today - timedelta(days=24), "Cloud", "Infra", 10_000),
        TransactionSignal("3", today - timedelta(days=2), "Cloud", "Infra", 50_000),
        TransactionSignal("4", today - timedelta(days=1), "Cloud", "Infra", 50_000),
    ]

    findings = detect_spend_spikes(transactions)
    assert findings
    assert findings[0]["type"] == "spend_spike"


def test_detect_subscription_creep() -> None:
    today = date.today()
    transactions = [
        TransactionSignal("1", today - timedelta(days=60), "SaaS Tool", "Software", 10_000),
        TransactionSignal("2", today - timedelta(days=30), "SaaS Tool", "Software", 11_000),
        TransactionSignal("3", today - timedelta(days=1), "SaaS Tool", "Software", 13_000),
    ]

    findings = detect_subscription_creep(transactions)
    assert len(findings) == 1
    assert findings[0]["type"] == "subscription_creep"
