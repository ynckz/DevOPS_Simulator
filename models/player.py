from sqlalchemy import Column, Integer, String
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
    last_incident = Column(String, nullable=True)
    last_activity = Column(String)
    
    skills = relationship("Skill", back_populates="player", cascade="all, delete-orphan")
