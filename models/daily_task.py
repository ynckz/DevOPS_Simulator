from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from models.database import Base

class DailyTask(Base):
    __tablename__ = 'daily_tasks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('players.user_id'))
    task_type = Column(String)  # "solve_incidents", "upgrade_skill", "buy_server"
    description = Column(String)
    target_amount = Column(Integer)
    current_amount = Column(Integer, default=0)
    reward_money = Column(Integer)
    reward_exp = Column(Integer)
    completed = Column(Boolean, default=False)
    claimed = Column(Boolean, default=False)  # Добавим флаг, получена ли награда
    date_created = Column(String)
    
    player = relationship("Player") 