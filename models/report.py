from sqlalchemy import Column, Integer, String, ForeignKey
from core.database import Base


class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    name = Column(String)
    format = Column(String)
    path = Column(String)
    generated_by = Column(String)