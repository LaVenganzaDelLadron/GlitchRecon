from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.responses import bad_request, not_found, success
from schemas.report import CreateReport
from services.report_service import destroy, index, show, store, update

router = APIRouter(
    prefix="/report",
    tags=["Report"],
)


@router.get("/")
async def list_reports(db: Session = Depends(get_db)):
    data = index(db)

    return success("Reports fetched successfully", data)


@router.post("/")
async def create_report(report: CreateReport, db: Session = Depends(get_db)):
    data = store(db, report.project_id, report.name, report.format, report.path, report.generated_by)

    if not data:
        bad_request("Invalid project_id")

    return success("Report created successfully", data)


@router.get("/{report_id}")
async def get_report_detail(report_id: int, db: Session = Depends(get_db)):
    data = show(db, report_id)

    if isinstance(data, dict):
        not_found(data["message"])

    return success("Report found successfully", data)


@router.put("/{report_id}")
async def update_report(report_id: int, report: CreateReport, db: Session = Depends(get_db)):
    data = update(db, report_id, report.project_id, report.name, report.format, report.path, report.generated_by)

    if not data:
        not_found("Report not found or invalid project_id")

    return success("Report updated successfully", data)


@router.delete("/{report_id}")
async def delete_report(report_id: int, db: Session = Depends(get_db)):
    data = destroy(db, report_id)

    if not data:
        not_found("Report not found")

    return success("Report deleted successfully", data)
