from fastapi import APIRouter

from app.routers.v1 import billing, dashboard, guidance, health, monitoring, payroll, plaid, scenarios, webhooks

api_router = APIRouter(prefix="/v1")
api_router.include_router(health.router, tags=["health"])
api_router.include_router(plaid.router, prefix="/plaid", tags=["plaid"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(scenarios.router, tags=["scenarios"])
api_router.include_router(payroll.router, prefix="/payroll", tags=["payroll"])
api_router.include_router(guidance.router, prefix="/guidance", tags=["guidance"])
