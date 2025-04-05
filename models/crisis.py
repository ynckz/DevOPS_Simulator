from sqlalchemy import Column, Integer, String, Boolean
from models.database import Base

class Crisis(Base):
    __tablename__ = 'crises'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    severity = Column(Integer)  # 1-5, где 5 - самый серьезный
    server_damage = Column(Integer)  # Урон здоровью серверов
    money_loss = Column(Integer)  # Потеря денег
    reputation_loss = Column(Integer)  # Потеря репутации 