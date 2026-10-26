from fastapi import FastAPI

from app.core.logging import RequestLoggingMiddleware, configure_logging
from app.routers import api_router

configure_logging()

app = FastAPI(title="Keystone API", version="0.1.0")
app.add_middleware(RequestLoggingMiddleware)
app.include_router(api_router)
