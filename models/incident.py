from sqlalchemy import Column, Integer, String

from models.database import Base

class Incident(Base):
    __tablename__ = 'incidents'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    difficulty = Column(Integer)
    reward = Column(Integer)