from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from core.database import Base

class Scan(Base):
    __tablename__ = 'scans'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    target_id = Column(Integer, ForeignKey('targets.id'))
    scanner = Column(String)
    status = Column(String)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)