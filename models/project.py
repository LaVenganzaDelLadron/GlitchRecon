from sqlalchemy import Column, Integer, String, ForeignKey
from core.database import Base


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    description = Column(String)
    scope = Column(String)
    status = Column(String)
    