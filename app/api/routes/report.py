"""Report API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_scan_service
from app.models.schemas import Report
from services.scan_service import ScanService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{scan_id}", response_model=Report)
async def get_report(
    scan_id: str,
    service: ScanService = Depends(get_scan_service),
) -> Report:
    """Retrieve the completed report for a scan."""

    report = await service.get_report(scan_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report
