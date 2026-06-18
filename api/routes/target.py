from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.responses import bad_request, not_found, success
from schemas.target import CreateTarget
from services.target_service import destroy, index, show, store, update

router = APIRouter(
    prefix="/target",
    tags=["Target"],
)


@router.get("/")
async def list_targets(db: Session = Depends(get_db)):
    data = index(db)

    return success("Successfully fetch target", data)


@router.post("/")
async def create_target(target: CreateTarget, db: Session = Depends(get_db)):
    data = store(db, target.project_id, target.type, target.value, target.notes)

    if not data:
        bad_request("Target for this project already exists")

    return success("Target created successfully", data)


@router.get("/{target_id}")
async def get_target_detail(target_id: int, db: Session = Depends(get_db)):
    data = show(db, target_id)

    if isinstance(data, dict):
        not_found(data["message"])

    return success("Target found successfully", data)


@router.put("/{target_id}")
async def update_target(target_id: int, target: CreateTarget, db: Session = Depends(get_db)):
    data = update(db, target_id, target.project_id, target.type, target.value, target.notes)

    if not data:
        not_found("Target not found or invalid project_id")

    return success("Target updated successfully", data)


@router.delete("/{target_id}")
async def delete_target(target_id: int, db: Session = Depends(get_db)):
    data = destroy(db, target_id)

    if not data:
        not_found("Target not found")

    return success("Target deleted successfully", data)
