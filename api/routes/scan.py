from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from api.dependencies import get_db
from schemas.scan import CreateScan
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


@router.delete("/{scan_id}")
async def delete_scan(scan_id: int, db: Session = Depends(get_db)):
    data = destroy(db, scan_id)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")

    return {"message": "Scan deleted successfully", "data": data}
