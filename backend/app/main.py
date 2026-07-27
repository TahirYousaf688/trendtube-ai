"""TrendTube AI - Main Application Entry Point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes import (
    admin_router,
    analytics_router,
    assets_router,
    auth_router,
    billing_router,
    channels_router,
    health_router,
    notifications_router,
    research_router,
    scripts_router,
    seo_router,
    thumbnails_router,
    trends_router,
    users_router,
    videos_router,
    webhooks_router,
    workflows_router,
)
from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
)
from app.core.logging import setup_logging
from fastapi.exceptions import RequestValidationError

# Setup structured logging
setup_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered content factory for YouTube automation",
    docs_url="/docs" if settings.env != "production" else None,
    redoc_url="/redoc" if settings.env != "production" else None,
    openapi_url="/openapi.json" if settings.env != "production" else None,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.env == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(health_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(channels_router, prefix="/api/v1")
app.include_router(trends_router, prefix="/api/v1")
app.include_router(research_router, prefix="/api/v1")
app.include_router(scripts_router, prefix="/api/v1")
app.include_router(videos_router, prefix="/api/v1")
app.include_router(assets_router, prefix="/api/v1")
app.include_router(thumbnails_router, prefix="/api/v1")
app.include_router(seo_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(billing_router, prefix="/api/v1")
app.include_router(workflows_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")


@app.get("/")
def root() -> dict:
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.env,
        "docs": "/docs",
        "openapi": "/openapi.json",
    }




