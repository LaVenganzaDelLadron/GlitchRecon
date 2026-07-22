"""FastAPI route modules."""

from app.api.routes.report import router as report_router
from app.api.routes.scan import router as scan_router

__all__ = ["report_router", "scan_router"]
