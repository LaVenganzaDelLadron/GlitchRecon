from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
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
    proposed_plan = Column(Text)
    executed_command = Column(Text)
    stdout = Column(Text)
    stderr = Column(Text)
    return_code = Column(Integer)
    error_message = Column(Text)
    approved_at = Column(DateTime)
