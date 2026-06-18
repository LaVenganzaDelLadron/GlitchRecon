from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette import status

from api.dependencies import get_db
from schemas.scan import CreateScan, PlanScan
from services.scan_orchestrator import (
    ScanOrchestrationError,
    approve_scan,
    cancel_running_scan,
    create_scan_plan,
    get_scan_logs,
    get_scan_status,
    list_child_scans,
    run_approved_scan,
)
from services.scan_service import destroy, index, show, store, update

router = APIRouter(
    prefix="/scan",
    tags=["Scan"],
)


@router.get("/")
async def list_scans(db: Session = Depends(get_db)):
    data = index(db)

    if isinstance(data, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=data["message"])

    return {"message": "Scans fetched successfully", "data": data}


@router.post("/")
async def create_scan(scan: CreateScan, db: Session = Depends(get_db)):
    data = store(db, scan.project_id, scan.target_id, scan.scanner, scan.status, scan.started_at, scan.finished_at)

    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project_id or target_id")

    return {"message": "Scan created successfully", "data": data}


@router.post("/plan")
def plan_scan(scan: PlanScan, db: Session = Depends(get_db)):
    try:
        data = create_scan_plan(db, scan.project_id, scan.target_id, scan.goal, scan.provider)
    except ScanOrchestrationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    return {"message": "Scan plan created and waiting for approval", "data": data}


@router.get("/{scan_id}")
async def get_scan_detail(scan_id: int, db: Session = Depends(get_db)):
    data = show(db, scan_id)

    if isinstance(data, dict):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=data["message"])

    return {"message": "Scan found successfully", "data": data}


@router.put("/{scan_id}")
async def update_scan(scan_id: int, scan: CreateScan, db: Session = Depends(get_db)):
    data = update(db, scan_id, scan.project_id, scan.target_id, scan.scanner, scan.status, scan.started_at, scan.finished_at)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found or invalid foreign key")

    return {"message": "Scan updated successfully", "data": data}


@router.post("/{scan_id}/approve")
async def approve_scan_plan(scan_id: int, db: Session = Depends(get_db)):
    try:
        data = approve_scan(db, scan_id)
    except ScanOrchestrationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return {"message": "Scan approved successfully", "data": data}


@router.post("/{scan_id}/run")
async def run_scan(scan_id: int, db: Session = Depends(get_db)):
    try:
        data = run_approved_scan(db, scan_id)
    except ScanOrchestrationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "message": "Scan started in the background",
            "data": {
                "scan_id": data.id,
                "status": data.status,
                "pid": data.pid,
                "status_url": f"/scan/{data.id}/status",
                "logs_url": f"/scan/{data.id}/logs",
                "children_url": f"/scan/{data.id}/children",
            },
        },
    )


@router.get("/{scan_id}/children")
async def read_scan_children(scan_id: int, db: Session = Depends(get_db)):
    try:
        data = list_child_scans(db, scan_id)
    except ScanOrchestrationError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return {"message": "Child scans fetched successfully", "data": data}


@router.get("/{scan_id}/status")
async def read_scan_status(scan_id: int, db: Session = Depends(get_db)):
    try:
        data = get_scan_status(db, scan_id)
    except ScanOrchestrationError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return {"message": "Scan status fetched successfully", "data": data}


@router.get("/{scan_id}/logs")
async def read_scan_logs(scan_id: int, db: Session = Depends(get_db)):
    try:
        data = get_scan_logs(db, scan_id)
    except ScanOrchestrationError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return {"message": "Scan logs fetched successfully", "data": data}


@router.post("/{scan_id}/cancel")
async def cancel_scan(scan_id: int, db: Session = Depends(get_db)):
    try:
        data = cancel_running_scan(db, scan_id)
    except ScanOrchestrationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return {"message": "Scan cancelled successfully", "data": data}


@router.delete("/{scan_id}")
async def delete_scan(scan_id: int, db: Session = Depends(get_db)):
    data = destroy(db, scan_id)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")

    return {"message": "Scan deleted successfully", "data": data}
