from sqlalchemy import Column, Integer, String, JSON

from models.database import Base

class Incident(Base):
    __tablename__ = 'incidents'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    difficulty = Column(Integer)
    reward = Column(Integer)
    possible_solutions = Column(JSON, nullable=True)  # Добавляем nullable=True
    time_sensitive = Column(Integer, default=0)  # Добавляем default=0