from sqlalchemy import Column, Integer, String, ForeignKey
from core.database import Base

class AI_Analysis(Base):
    __tablename__ = 'ai_analysis'
    id = Column(Integer, primary_key=True)
    finding_id = Column(Integer, ForeignKey('finding.id'))
    model = Column(String)
    prompt = Column(String)
    response = Column(String)