from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_current_user, get_db
from api.responses import bad_request, not_found, success
from models.users import Users
from schemas.project import CreateProject
from services.project_service import destroy, index, show, store, update

router = APIRouter(
    prefix="/project",
    tags=["Project"],
)


@router.get("/")
async def list_projects(db: Session = Depends(get_db)):
    data = index(db)

    return success("Projects fetched successfully", data)


@router.post("/")
async def create_project(
    project: CreateProject,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    data = store(db, current_user.id, project.name, project.description, project.scope, project.status)

    if not data:
        bad_request("Invalid project data")

    return success("Project created successfully", data)


@router.get("/{project_id}")
async def get_project_detail(project_id: int, db: Session = Depends(get_db)):
    data = show(db, project_id)

    if isinstance(data, dict):
        not_found(data["message"])

    return success("Project found successfully", data)


@router.put("/{project_id}")
async def update_project(
    project_id: int,
    project: CreateProject,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    data = update(db, project_id, current_user.id, project.name, project.description, project.scope, project.status)

    if not data:
        not_found("Project not found")

    return success("Project updated successfully", data)


@router.delete("/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    data = destroy(db, project_id)

    if not data:
        not_found("Project not found")

    return success("Project deleted successfully", data)
