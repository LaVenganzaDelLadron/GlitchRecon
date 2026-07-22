"""ASGI application entry point for GlitchRecon."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import report_router, scan_router


def create_app() -> FastAPI:
    """Create and configure the GlitchRecon HTTP application."""

    application = FastAPI(
        title="GlitchRecon API",
        version="0.4.0",
        description="AI-assisted, evidence-driven web vulnerability reporting.",
    )
    application.include_router(scan_router)
    application.include_router(report_router)
    return application


app = create_app()
