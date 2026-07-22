"""Scan API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl

from app.api.dependencies import get_scan_service
from app.models.schemas import Report, Scan
from services.scan_service import ScanExecutionError, ScanService

router = APIRouter(prefix="/scans", tags=["scans"])


class StartScanRequest(BaseModel):
    """Request body for initiating an authorized target scan."""

    target: HttpUrl


@router.post("", response_model=Report, status_code=status.HTTP_201_CREATED)
async def start_scan(
    request: StartScanRequest,
    service: ScanService = Depends(get_scan_service),
) -> Report:
    """Start a scan and return the completed report."""

    try:
        return await service.start_scan(str(request.target))
    except ScanExecutionError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("/{scan_id}", response_model=Scan)
async def get_scan(
    scan_id: str,
    service: ScanService = Depends(get_scan_service),
) -> Scan:
    """Retrieve an existing scan record."""

    scan = await service.get_scan(scan_id)
    if scan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return scan
