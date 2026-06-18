from sqlalchemy.orm import Session

from models.project import Project
from models.target import Target

def index(db: Session):
    return db.query(Target).all()


def store(db: Session, project_id: int, type: str, value: str, notes: str):
    if not db.query(Project).filter(Project.id == project_id).first():
        return None

    existing = db.query(Target).filter(Target.project_id == project_id).first()

    if existing:
        return None

    data = Target(project_id=project_id, type=type, value=value, notes=notes)

    db.add(data)
    db.commit()
    db.refresh(data)

    return data

def show(db: Session, target_id: int):
    data = db.query(Target).filter(Target.id == target_id).first()

    if data:
        return data
    else:
        return {
            "message": "Target not found"
        }

def update(db: Session, target_id: int, project_id: int, type: str, value: str, notes: str):
    data = db.query(Target).filter(Target.id == target_id).first()

    if data:
        if not db.query(Project).filter(Project.id == project_id).first():
            return None

        data.project_id = project_id
        data.type = type
        data.value = value
        data.notes = notes

        db.commit()
        db.refresh(data)

    return data

def destroy(db: Session, target_id: int):
    data = db.query(Target).filter(Target.id == target_id).first()
    if data:
        db.delete(data)
        db.commit()
    return data
