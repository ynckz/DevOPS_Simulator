from sqlalchemy import Column, Integer, String, JSON

from models.database import Base

class Incident(Base):
    __tablename__ = 'incidents'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    difficulty = Column(Integer)
    reward = Column(Integer)
    possible_solutions = Column(JSON)  # JSON список возможных решений с их эффективностью
    time_sensitive = Column(Integer, default=0)  # 0 - не ограничено по времени, >0 - максимальное время в секундах