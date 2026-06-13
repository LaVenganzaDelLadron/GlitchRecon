from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from api.dependencies import get_db
from schemas.finding import Finding
from services.finding_service import destroy, index, show, store, update

router = APIRouter(
    prefix="/finding",
    tags=["Finding"],
)


@router.get("/")
async def list_findings(db: Session = Depends(get_db)):
    data = index(db)

    if isinstance(data, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=data["message"])

    return {"message": "Findings fetched successfully", "data": data}


@router.post("/")
async def create_finding(finding: Finding, db: Session = Depends(get_db)):
    data = store(db, finding.scan_id, finding.title, finding.severity, finding.description, finding.evidence, finding.remediation, finding.cve, finding.cvss)

    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid scan_id")

    return {"message": "Finding created successfully", "data": data}


@router.get("/{finding_id}")
async def get_finding_detail(finding_id: int, db: Session = Depends(get_db)):
    data = show(db, finding_id)

    if isinstance(data, dict):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=data["message"])

    return {"message": "Finding found successfully", "data": data}


@router.put("/{finding_id}")
async def update_finding(finding_id: int, finding: Finding, db: Session = Depends(get_db)):
    data = update(db, finding_id, finding.scan_id, finding.title, finding.severity, finding.description, finding.evidence, finding.remediation, finding.cve, finding.cvss)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found or invalid scan_id")

    return {"message": "Finding updated successfully", "data": data}


@router.delete("/{finding_id}")
async def delete_finding(finding_id: int, db: Session = Depends(get_db)):
    data = destroy(db, finding_id)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")

    return {"message": "Finding deleted successfully", "data": data}
