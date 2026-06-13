from sqlalchemy import Column, Integer, String, ForeignKey
from core.database import Base

class Target(Base):
    __tablename__ = 'targets'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    type = Column(String)
    value = Column(String)
    notes = Column(String)