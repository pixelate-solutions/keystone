from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx
import jwt
from fastapi import HTTPException, status

from app.core.config import settings


@dataclass
class AuthContext:
    clerk_user_id: str
    clerk_org_id: str
    claims: dict[str, Any]


class ClerkVerifier:
    def __init__(self) -> None:
        self._jwks_cache: dict[str, Any] | None = None
        self._jwks_expires_at: float = 0

    async def _get_jwks(self) -> dict[str, Any]:
        now = time.time()
        if self._jwks_cache and now < self._jwks_expires_at:
            return self._jwks_cache

        if not settings.clerk_jwks_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="CLERK_JWKS_URL not configured",
            )

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.clerk_jwks_url)
            response.raise_for_status()
            self._jwks_cache = response.json()
            self._jwks_expires_at = now + 3600
            return self._jwks_cache

    async def verify(self, token: str) -> AuthContext:
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

        jwks = await self._get_jwks()
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token header")

        key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        if not key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Signing key not found")

        try:
            claims = jwt.decode(
                token,
                key=jwt.algorithms.RSAAlgorithm.from_jwk(key),
                algorithms=["RS256"],
                issuer=settings.clerk_issuer or None,
                options={"verify_aud": False},
            )
        except jwt.PyJWTError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

        clerk_user_id = claims.get("sub")
        clerk_org_id = claims.get("org_id") or claims.get("organization_id")

        if not clerk_user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid subject")

        if not clerk_org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Missing org_id claim",
            )

        return AuthContext(
            clerk_user_id=clerk_user_id,
            clerk_org_id=clerk_org_id,
            claims=claims,
        )


verifier = ClerkVerifier()
