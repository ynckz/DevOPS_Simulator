from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from models.database import Base

class Player(Base):
    __tablename__ = 'players'
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    money = Column(Integer, default=1000)
    servers = Column(Integer, default=1)
    server_health = Column(Float, default=100.0)  # Здоровье серверной инфраструктуры (%)
    reputation = Column(Integer, default=50)      # Репутация DevOps-инженера
    successful_fixes = Column(Integer, default=0) # Успешно решенные инциденты
    failed_fixes = Column(Integer, default=0)     # Проваленные инциденты
    last_incident = Column(String, nullable=True)
    last_activity = Column(String)
    
    skills = relationship("Skill", back_populates="player", cascade="all, delete-orphan")
