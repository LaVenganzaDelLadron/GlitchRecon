from sqlalchemy.orm import Session

from models.project import Project
from models.report import Report


def index(db: Session):
    return db.query(Report).all()


def store(db: Session, project_id: int, name: str, format: str, path: str, generated_by: str):
    if not db.query(Project).filter(Project.id == project_id).first():
        return None

    data = Report(
        project_id=project_id,
        name=name,
        format=format,
        path=path,
        generated_by=generated_by,
    )

    db.add(data)
    db.commit()
    db.refresh(data)

    return data


def show(db: Session, report_id: int):
    data = db.query(Report).filter(Report.id == report_id).first()

    if data:
        return data
    return {"message": "Report not found"}


def update(db: Session, report_id: int, project_id: int, name: str, format: str, path: str, generated_by: str):
    data = db.query(Report).filter(Report.id == report_id).first()

    if not data:
        return None

    if not db.query(Project).filter(Project.id == project_id).first():
        return None

    data.project_id = project_id
    data.name = name
    data.format = format
    data.path = path
    data.generated_by = generated_by

    db.commit()
    db.refresh(data)

    return data


def destroy(db: Session, report_id: int):
    data = db.query(Report).filter(Report.id == report_id).first()

    if data:
        db.delete(data)
        db.commit()

    return data
