from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from api.dependencies import get_db
from schemas.project import CreateProject
from services.project_service import destroy, index, show, store, update

router = APIRouter(
    prefix="/project",
    tags=["Project"],
)


@router.get("/")
async def list_projects(db: Session = Depends(get_db)):
    data = index(db)

    if isinstance(data, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=data["message"])

    return {"message": "Projects fetched successfully", "data": data}


@router.post("/")
async def create_project(project: CreateProject, db: Session = Depends(get_db)):
    data = store(db, project.owner_id, project.name, project.description, project.scope, project.status)

    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid owner_id or project data")

    return {"message": "Project created successfully", "data": data}


@router.get("/{project_id}")
async def get_project_detail(project_id: int, db: Session = Depends(get_db)):
    data = show(db, project_id)

    if isinstance(data, dict):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=data["message"])

    return {"message": "Project found successfully", "data": data}


@router.put("/{project_id}")
async def update_project(project_id: int, project: CreateProject, db: Session = Depends(get_db)):
    data = update(db, project_id, project.owner_id, project.name, project.description, project.scope, project.status)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or invalid owner_id")

    return {"message": "Project updated successfully", "data": data}


@router.delete("/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    data = destroy(db, project_id)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return {"message": "Project deleted successfully", "data": data}
