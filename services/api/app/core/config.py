from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "keystone-api"
    environment: str = "development"

    database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/keystone")
    redis_url: str = Field(default="redis://localhost:6379/0")

    clerk_jwks_url: str = ""
    clerk_issuer: str = ""

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_pro_price_id: str = ""

    plaid_client_id: str = ""
    plaid_secret: str = ""
    plaid_env: str = "sandbox"
    plaid_sync_days: int = 90

    ai_provider: str = "mock"
    ai_api_key: str = ""
    feature_ai_guidance: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
