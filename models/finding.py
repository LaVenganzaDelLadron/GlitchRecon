from sqlalchemy import Column, Integer, String, ForeignKey
from core.database import Base

class Finding(Base):
    __tablename__ = 'findings'
    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey('scans.id'))
    title = Column(String)
    severity = Column(String)
    description = Column(String)
    evidence = Column(String)
    remediation = Column(String)
    cve = Column(String)
    cvss = Column(String)
    