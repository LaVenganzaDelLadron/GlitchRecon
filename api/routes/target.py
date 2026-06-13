from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from api.dependencies import get_db
from schemas.target import CreateTarget
from services.target_service import destroy, index, show, store, update

router = APIRouter(
    prefix="/target",
    tags=["Target"],
)


@router.get("/")
async def list_targets(db: Session = Depends(get_db)):
    data = index(db)

    if isinstance(data, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=data["message"])

    return {
        "message": "Successfully fetch target",
        "data": data,
    }


@router.post("/")
async def create_target(target: CreateTarget, db: Session = Depends(get_db)):
    data = store(db, target.project_id, target.type, target.value, target.notes)

    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Target for this project already exists")

    return {
        "message": "Target created successfully",
        "data": data,
    }


@router.get("/{target_id}")
async def get_target_detail(target_id: int, db: Session = Depends(get_db)):
    data = show(db, target_id)

    if isinstance(data, dict):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=data["message"])

    return {
        "message": "Target found successfully",
        "data": data,
    }


@router.put("/{target_id}")
async def update_target(target_id: int, target: CreateTarget, db: Session = Depends(get_db)):
    data = update(db, target_id, target.type, target.value, target.notes)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")

    return {
        "message": "Target updated successfully",
        "data": data,
    }


@router.delete("/{target_id}")
async def delete_target(target_id: int, db: Session = Depends(get_db)):
    data = destroy(db, target_id)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")

    return {
        "message": "Target deleted successfully",
        "data": data,
    }


