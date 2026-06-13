from sqlalchemy.orm import Session

from models.project import Project
from models.users import Users


def index(db: Session):
    data = db.query(Project).all()

    if data:
        return data
    return {"message": "No projects found"}


def store(db: Session, owner_id: int, name: str, description: str, scope: str, status: str):
    if not db.query(Users).filter(Users.id == owner_id).first():
        return None

    data = Project(
        owner_id=owner_id,
        name=name,
        description=description,
        scope=scope,
        status=status,
    )

    db.add(data)
    db.commit()
    db.refresh(data)

    return data


def show(db: Session, project_id: int):
    data = db.query(Project).filter(Project.id == project_id).first()

    if data:
        return data
    return {"message": "Project not found"}


def update(db: Session, project_id: int, owner_id: int, name: str, description: str, scope: str, status: str):
    data = db.query(Project).filter(Project.id == project_id).first()

    if not data:
        return None

    if not db.query(Users).filter(Users.id == owner_id).first():
        return None

    data.owner_id = owner_id
    data.name = name
    data.description = description
    data.scope = scope
    data.status = status

    db.commit()
    db.refresh(data)

    return data


def destroy(db: Session, project_id: int):
    data = db.query(Project).filter(Project.id == project_id).first()

    if data:
        db.delete(data)
        db.commit()

    return data
