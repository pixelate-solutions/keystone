from __future__ import annotations

import asyncio
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal
from app.models.models import (
    Account,
    Anomaly,
    Obligation,
    PayrollPlan,
    Role,
    Scenario,
    Transaction,
    User,
)

DEMO_ORG = "org_demo"
DEMO_USER = "user_demo"


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        # Keep seed idempotent by clearing demo org rows first.
        for model in [
            Transaction,
            Account,
            Obligation,
            PayrollPlan,
            Role,
            Scenario,
            Anomaly,
            User,
        ]:
            await session.execute(delete(model).where(model.clerk_org_id == DEMO_ORG))

        session.add(User(clerk_user_id=DEMO_USER, clerk_org_id=DEMO_ORG, email="demo@keystone.local"))

        operating = Account(
            clerk_org_id=DEMO_ORG,
            plaid_account_id="manual-operating",
            name="Operating Account",
            type="depository",
            subtype="checking",
            mask="1234",
            currency_code="USD",
            current_balance_cents=8200000,
            available_balance_cents=8100000,
        )
        reserve = Account(
            clerk_org_id=DEMO_ORG,
            plaid_account_id="manual-reserve",
            name="Reserve Account",
            type="depository",
            subtype="savings",
            mask="4455",
            currency_code="USD",
            current_balance_cents=2600000,
            available_balance_cents=2600000,
        )
        session.add_all([operating, reserve])
        await session.flush()

        today = date.today()
        demo_txns = [
            Transaction(
                clerk_org_id=DEMO_ORG,
                account_id=operating.account_id,
                date=today - timedelta(days=1),
                name="Payroll Batch",
                amount_cents=240000,
                merchant="Payroll Processor",
                category="Payroll",
                currency_code="USD",
                is_pending=False,
            ),
            Transaction(
                clerk_org_id=DEMO_ORG,
                account_id=operating.account_id,
                date=today - timedelta(days=3),
                name="Cloud Services",
                amount_cents=54000,
                merchant="Cloud Vendor",
                category="Infrastructure",
                currency_code="USD",
                is_pending=False,
            ),
            Transaction(
                clerk_org_id=DEMO_ORG,
                account_id=operating.account_id,
                date=today - timedelta(days=6),
                name="Customer Receipt",
                amount_cents=-360000,
                merchant="Customer ACH",
                category="Revenue",
                currency_code="USD",
                is_pending=False,
            ),
        ]
        session.add_all(demo_txns)

        obligations = [
            Obligation(
                clerk_org_id=DEMO_ORG,
                type="payroll",
                name="Bi-weekly payroll",
                amount_cents=245000,
                currency_code="USD",
                due_date=today + timedelta(days=5),
                cadence="biweekly",
            ),
            Obligation(
                clerk_org_id=DEMO_ORG,
                type="vendor",
                name="Infrastructure invoice",
                amount_cents=64000,
                currency_code="USD",
                due_date=today + timedelta(days=9),
                cadence="monthly",
            ),
            Obligation(
                clerk_org_id=DEMO_ORG,
                type="debt",
                name="Credit facility payment",
                amount_cents=50000,
                currency_code="USD",
                due_date=today + timedelta(days=19),
                cadence="monthly",
            ),
        ]
        session.add_all(obligations)

        plan = PayrollPlan(
            clerk_org_id=DEMO_ORG,
            baseline_monthly_cents=490000,
            fully_loaded_multiplier=1.22,
            currency_code="USD",
        )
        session.add(plan)

        roles = [
            Role(
                clerk_org_id=DEMO_ORG,
                title="Senior Engineer",
                monthly_cost_cents=21000,
                start_date=today + timedelta(days=35),
                is_planned=True,
                currency_code="USD",
            ),
            Role(
                clerk_org_id=DEMO_ORG,
                title="Customer Success Manager",
                monthly_cost_cents=14500,
                start_date=today + timedelta(days=42),
                is_planned=True,
                currency_code="USD",
            ),
        ]
        session.add_all(roles)

        session.add(
            Scenario(
                clerk_org_id=DEMO_ORG,
                name="Conservative",
                revenue_delta_pct=-10,
                vendor_terms_shift_days=10,
                created_at=datetime.now(UTC),
            )
        )

        session.add(
            Anomaly(
                clerk_org_id=DEMO_ORG,
                type="spend_spike",
                severity="medium",
                confidence="high",
                title="Spend spike in infrastructure",
                explanation="Infrastructure spend is 2.3x trailing weekly average.",
                related_txn_ids=[],
            )
        )

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
    print("Seed completed for org_demo/user_demo")
