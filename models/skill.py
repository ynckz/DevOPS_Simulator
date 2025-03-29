from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models.database import Base

class Skill(Base):
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('players.user_id'))
    skill_name = Column(String)
    skill_level = Column(Integer, default=1)
    
    player = relationship("Player", back_populates="skills")