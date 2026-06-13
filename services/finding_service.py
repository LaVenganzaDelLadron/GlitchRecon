from sqlalchemy.orm import Session

from models.finding import Finding
from models.scan import Scan


def index(db: Session):
    data = db.query(Finding).all()

    if data:
        return data
    return {"message": "No findings found"}


def store(db: Session, scan_id: int, title: str, severity: str, description: str, evidence: str, remediation: str, cve: str, cvss: str):
    if not db.query(Scan).filter(Scan.id == scan_id).first():
        return None

    data = Finding(
        scan_id=scan_id,
        title=title,
        severity=severity,
        description=description,
        evidence=evidence,
        remediation=remediation,
        cve=cve,
        cvss=cvss,
    )

    db.add(data)
    db.commit()
    db.refresh(data)

    return data


def show(db: Session, finding_id: int):
    data = db.query(Finding).filter(Finding.id == finding_id).first()

    if data:
        return data
    return {"message": "Finding not found"}


def update(db: Session, finding_id: int, scan_id: int, title: str, severity: str, description: str, evidence: str, remediation: str, cve: str, cvss: str):
    data = db.query(Finding).filter(Finding.id == finding_id).first()

    if not data:
        return None

    if not db.query(Scan).filter(Scan.id == scan_id).first():
        return None

    data.scan_id = scan_id
    data.title = title
    data.severity = severity
    data.description = description
    data.evidence = evidence
    data.remediation = remediation
    data.cve = cve
    data.cvss = cvss

    db.commit()
    db.refresh(data)

    return data


def destroy(db: Session, finding_id: int):
    data = db.query(Finding).filter(Finding.id == finding_id).first()

    if data:
        db.delete(data)
        db.commit()

    return data
