import asyncio
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.database import engine, Base
from core.schema_migrations import ensure_scan_columns
from api.routes.auth import router as auth_router
from api.routes.target import router as target_router
from api.routes.project import router as project_router
from api.routes.scan import router as scan_router
from api.routes.report import router as report_router
from api.routes.finding import router as finding_router
import models.users
import models.project
import models.target
import models.scan
import models.report
import models.finding


Base.metadata.create_all(bind=engine)
ensure_scan_columns(engine)
app = FastAPI()

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["OPTIONS", "GET", "POST", "PUT", "DELETE"],
    allow_headers=["authorization", "content-type"],
)

EXEMPT_PATHS = {"/", "/docs", "/openapi.json", "/redoc", "/auth/register", "/auth/login"}
REQUEST_HARD_TIMEOUT = float(os.getenv("REQUEST_HARD_TIMEOUT", "45"))
TIMEOUT_EXEMPT_PREFIXES = (
    "/docs",
    "/openapi.json",
    "/redoc",
)


def _is_timeout_exempt(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in TIMEOUT_EXEMPT_PREFIXES) or path.endswith("/status") or path.endswith("/logs")


@app.middleware("http")
async def request_timeout_middleware(request: Request, call_next):
    path = request.url.path or ""
    if _is_timeout_exempt(path):
        return await call_next(request)

    try:
        return await asyncio.wait_for(call_next(request), timeout=REQUEST_HARD_TIMEOUT)
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=504,
            content={"detail": f"Request exceeded {REQUEST_HARD_TIMEOUT:.0f}s timeout"},
        )


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    if request.url.path in EXEMPT_PATHS:
        return await call_next(request)

    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Authentication required"})

    token = auth_header.split(" ", 1)[1]
    from services.auth_service import decode_token

    payload = decode_token(token)
    if not payload or not payload.get("sub"):
        return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

    request.state.user = payload
    response = await call_next(request)
    return response


@app.get("/")
async def root():
    return {"status": "Alive"}


app.include_router(auth_router)
app.include_router(target_router)
app.include_router(project_router)
app.include_router(scan_router)
app.include_router(report_router)
app.include_router(finding_router)
