from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.responses import bad_request, not_found, success
from schemas.finding import Finding
from services.finding_service import destroy, index, show, store, update

router = APIRouter(
    prefix="/finding",
    tags=["Finding"],
)


@router.get("/")
async def list_findings(db: Session = Depends(get_db)):
    data = index(db)

    return success("Findings fetched successfully", data)


@router.post("/")
async def create_finding(finding: Finding, db: Session = Depends(get_db)):
    data = store(db, finding.scan_id, finding.title, finding.severity, finding.description, finding.evidence, finding.remediation, finding.cve, finding.cvss)

    if not data:
        bad_request("Invalid scan_id")

    return success("Finding created successfully", data)


@router.get("/{finding_id}")
async def get_finding_detail(finding_id: int, db: Session = Depends(get_db)):
    data = show(db, finding_id)

    if isinstance(data, dict):
        not_found(data["message"])

    return success("Finding found successfully", data)


@router.put("/{finding_id}")
async def update_finding(finding_id: int, finding: Finding, db: Session = Depends(get_db)):
    data = update(db, finding_id, finding.scan_id, finding.title, finding.severity, finding.description, finding.evidence, finding.remediation, finding.cve, finding.cvss)

    if not data:
        not_found("Finding not found or invalid scan_id")

    return success("Finding updated successfully", data)


@router.delete("/{finding_id}")
async def delete_finding(finding_id: int, db: Session = Depends(get_db)):
    data = destroy(db, finding_id)

    if not data:
        not_found("Finding not found")

    return success("Finding deleted successfully", data)
