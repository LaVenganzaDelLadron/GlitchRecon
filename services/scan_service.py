import datetime

from sqlalchemy.orm import Session

from models.project import Project
from models.scan import Scan
from models.target import Target


def index(db: Session):
    data = db.query(Scan).all()

    if data:
        return data
    return {"message": "No scans found"}


def store(db: Session, project_id: int, target_id: int, scanner: str, status: str, started_at: datetime, finished_at: datetime):
    if not db.query(Project).filter(Project.id == project_id).first():
        return None

    if not db.query(Target).filter(Target.id == target_id).first():
        return None

    data = Scan(
        project_id=project_id,
        target_id=target_id,
        scanner=scanner,
        status=status,
        started_at=started_at,
        finished_at=finished_at,
    )

    db.add(data)
    db.commit()
    db.refresh(data)

    return data


def show(db: Session, scan_id: int):
    data = db.query(Scan).filter(Scan.id == scan_id).first()

    if data:
        return data
    return {"message": "No scans found"}


def update(db: Session, scan_id: int, project_id: int, target_id: int, scanner: str, status: str, started_at: datetime, finished_at: datetime):
    data = db.query(Scan).filter(Scan.id == scan_id).first()

    if not data:
        return None

    if not db.query(Project).filter(Project.id == project_id).first():
        return None

    if not db.query(Target).filter(Target.id == target_id).first():
        return None

    data.project_id = project_id
    data.target_id = target_id
    data.scanner = scanner
    data.status = status
    data.started_at = started_at
    data.finished_at = finished_at

    db.commit()
    db.refresh(data)

    return data


def destroy(db: Session, scan_id: int):
    data = db.query(Scan).filter(Scan.id == scan_id).first()

    if data:
        db.delete(data)
        db.commit()

    return data

