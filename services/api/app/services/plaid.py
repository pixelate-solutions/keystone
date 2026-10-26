from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.models import Account, Connection, Transaction


def plaid_base_url() -> str:
    env_map = {
        "sandbox": "https://sandbox.plaid.com",
        "development": "https://development.plaid.com",
        "production": "https://production.plaid.com",
    }
    return env_map.get(settings.plaid_env, env_map["sandbox"])


async def plaid_request(path: str, payload: dict) -> dict:
    body = {
        "client_id": settings.plaid_client_id,
        "secret": settings.plaid_secret,
        **payload,
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(f"{plaid_base_url()}{path}", json=body)
        response.raise_for_status()
        return response.json()


async def create_link_token(clerk_user_id: str, clerk_org_id: str) -> str:
    result = await plaid_request(
        "/link/token/create",
        {
            "client_name": "Keystone",
            "country_codes": ["US"],
            "language": "en",
            "products": ["transactions"],
            "user": {"client_user_id": f"{clerk_org_id}:{clerk_user_id}"},
        },
    )
    return result["link_token"]


async def exchange_public_token(
    session: AsyncSession,
    clerk_org_id: str,
    public_token: str,
    institution_name: str | None,
) -> Connection:
    result = await plaid_request(
        "/item/public_token/exchange",
        {
            "public_token": public_token,
        },
    )

    connection = Connection(
        clerk_org_id=clerk_org_id,
        plaid_item_id=result["item_id"],
        access_token=result["access_token"],
        institution=institution_name,
        status="pending",
    )
    session.add(connection)
    await session.commit()
    await session.refresh(connection)
    return connection


async def sync_connection_data(
    session: AsyncSession,
    connection_id: str,
    clerk_org_id: str,
    days_back: int,
) -> None:
    connection = await session.get(Connection, connection_id)
    if not connection or connection.clerk_org_id != clerk_org_id:
        raise ValueError("Connection not found")

    connection.status = "syncing"
    connection.last_error = None
    await session.commit()

    try:
        balances = await plaid_request(
            "/accounts/balance/get",
            {
                "access_token": connection.access_token,
            },
        )

        for account_data in balances.get("accounts", []):
            currency = account_data.get("balances", {}).get("iso_currency_code")
            if currency != "USD":
                continue

            plaid_account_id = account_data["account_id"]
            stmt = select(Account).where(Account.plaid_account_id == plaid_account_id)
            existing = (await session.execute(stmt)).scalar_one_or_none()

            current_balance = account_data.get("balances", {}).get("current") or 0
            available_balance = account_data.get("balances", {}).get("available")

            if existing:
                existing.name = account_data.get("name", existing.name)
                existing.type = account_data.get("type", existing.type)
                existing.subtype = account_data.get("subtype")
                existing.mask = account_data.get("mask")
                existing.current_balance_cents = int(current_balance * 100)
                existing.available_balance_cents = (
                    int(available_balance * 100) if available_balance is not None else None
                )
            else:
                session.add(
                    Account(
                        clerk_org_id=clerk_org_id,
                        connection_id=connection.connection_id,
                        plaid_account_id=plaid_account_id,
                        name=account_data.get("name", "Account"),
                        type=account_data.get("type", "depository"),
                        subtype=account_data.get("subtype"),
                        mask=account_data.get("mask"),
                        currency_code="USD",
                        current_balance_cents=int(current_balance * 100),
                        available_balance_cents=(
                            int(available_balance * 100) if available_balance is not None else None
                        ),
                    )
                )

        start_date = (date.today() - timedelta(days=days_back)).isoformat()
        end_date = date.today().isoformat()
        txns_response = await plaid_request(
            "/transactions/get",
            {
                "access_token": connection.access_token,
                "start_date": start_date,
                "end_date": end_date,
                "options": {"count": 500, "offset": 0},
            },
        )

        accounts = await session.execute(
            select(Account).where(Account.connection_id == connection.connection_id)
        )
        accounts_by_plaid = {a.plaid_account_id: a for a in accounts.scalars().all()}

        for txn in txns_response.get("transactions", []):
            currency = txn.get("iso_currency_code")
            if currency != "USD":
                continue

            account = accounts_by_plaid.get(txn.get("account_id"))
            if not account:
                continue

            plaid_transaction_id = txn.get("transaction_id")
            existing_stmt = select(Transaction).where(
                Transaction.plaid_transaction_id == plaid_transaction_id
            )
            existing_txn = (await session.execute(existing_stmt)).scalar_one_or_none()

            amount_cents = int(float(txn.get("amount", 0)) * 100)
            payload = {
                "clerk_org_id": clerk_org_id,
                "account_id": account.account_id,
                "plaid_transaction_id": plaid_transaction_id,
                "date": date.fromisoformat(txn["date"]),
                "name": txn.get("name", "Transaction"),
                "amount_cents": amount_cents,
                "currency_code": "USD",
                "merchant": txn.get("merchant_name"),
                "category": ", ".join(txn.get("category", [])) if txn.get("category") else None,
                "is_pending": bool(txn.get("pending", False)),
                "raw_json": txn,
            }

            if existing_txn:
                for key, value in payload.items():
                    setattr(existing_txn, key, value)
            else:
                session.add(Transaction(**payload))

        connection.status = "ready"
        connection.last_error = None
        connection.last_sync_at = datetime.now(UTC)
        await session.commit()
    except Exception as exc:  # pragma: no cover
        connection.status = "error"
        connection.last_error = str(exc)
        await session.commit()
        raise
