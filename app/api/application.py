"""ASGI application entry point for GlitchRecon."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

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

    @application.get("/", include_in_schema=False)
    async def dashboard() -> FileResponse:
        """Serve the single-page scan dashboard."""

        return FileResponse(Path(__file__).parents[2] / "index.html")

    return application


app = create_app()
