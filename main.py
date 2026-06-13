from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from core.database import engine, Base
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
app = FastAPI()

EXEMPT_PATHS = {"/", "/docs", "/openapi.json", "/redoc", "/auth/register", "/auth/login"}


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
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