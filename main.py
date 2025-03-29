import asyncio
import logging
import random
import time
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, func, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session

from config import BOT_TOKEN
from models.database import Base, engine
from services.incident_service import init_default_incidents
from handlers import setup_routers

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)

# Настройка SQLAlchemy
engine = create_engine('sqlite:///devops_simulator.db')
Base = declarative_base()
SessionMaker = sessionmaker(bind=engine)

# Временное хранилище для данных пользователей
user_data: Dict[int, Dict[str, Any]] = {}

# Модели SQLAlchemy
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

class Skill(Base):
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('players.user_id'))
    skill_name = Column(String)
    skill_level = Column(Integer, default=1)
    
    player = relationship("Player", back_populates="skills")

class Incident(Base):
    __tablename__ = 'incidents'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    difficulty = Column(Integer)
    reward = Column(Integer)

# Инициализация базы данных
async def init_db():
    """Инициализация базы данных и заполнение начальными данными"""
    Base.metadata.create_all(engine)
    await init_default_incidents()

# Получение или создание игрока
async def get_or_create_player(user_id: int, username: str) -> Player:
    with SessionMaker() as session:
        player = session.query(Player).filter(Player.user_id == user_id).first()
        
        if not player:
            player = Player(
                user_id=user_id,
                username=username,
                last_activity=datetime.now().isoformat()
            )
            session.add(player)
            session.commit()
            
            # Создаем начальные навыки
            basic_skills = [
                Skill(user_id=user_id, skill_name='Linux', skill_level=1),
                Skill(user_id=user_id, skill_name='Networking', skill_level=1),
                Skill(user_id=user_id, skill_name='Docker', skill_level=1),
                Skill(user_id=user_id, skill_name='CI/CD', skill_level=1),
                Skill(user_id=user_id, skill_name='Monitoring', skill_level=1)
            ]
            session.add_all(basic_skills)
            session.commit()
            
            # Перезагружаем игрока, чтобы получить связанные навыки
            session.refresh(player)
        
        return player

# Получение профиля игрока
async def get_player_profile(user_id: int) -> Tuple[Optional[Player], List[Skill]]:
    with SessionMaker() as session:
        player = session.query(Player).filter(Player.user_id == user_id).first()
        
        if player:
            skills = session.query(Skill).filter(Skill.user_id == user_id).all()
            return player, skills
        return None, []

# Обновление опыта и уровня
async def update_experience(user_id: int, exp_gain: int) -> Tuple[int, int, bool]:
    with SessionMaker() as session:
        player = session.query(Player).filter(Player.user_id == user_id).first()
        
        if not player:
            return 1, 0, False
        
        player.experience += exp_gain
        level_up = False
        
        # Формула для повышения уровня: 100 * текущий_уровень
        next_level_exp = 100 * player.level
        
        if player.experience >= next_level_exp:
            player.level += 1
            level_up = True
        
        player.last_activity = datetime.now().isoformat()
        session.commit()
        
        return player.level, player.experience, level_up

# Генерация случайного инцидента
async def generate_incident(user_id: int) -> Optional[Incident]:
    with SessionMaker() as session:
        player = session.query(Player).filter(Player.user_id == user_id).first()
        
        if not player:
            return None
        
        player_level = player.level
        
        # Получаем инциденты, соответствующие уровню игрока +/- 1
        min_difficulty = max(1, player_level - 1)
        max_difficulty = player_level + 1
        
        incidents = session.query(Incident).filter(
            Incident.difficulty.between(min_difficulty, max_difficulty)
        ).all()
        
        if not incidents:
            return None
        
        return random.choice(incidents)

# Обработка инцидента
async def solve_incident(user_id: int, incident_id: int, solution_time: float) -> Tuple[int, int, bool]:
    with SessionMaker() as session:
        incident = session.query(Incident).filter(Incident.id == incident_id).first()
        player = session.query(Player).filter(Player.user_id == user_id).first()
        
        if not incident or not player:
            return 0, 0, False
        
        difficulty = incident.difficulty
        base_reward = incident.reward
        
        # Бонус от количества серверов
        server_bonus = 1 + (player.servers - 1) * 0.1
        
        # Расчет награды в зависимости от времени решения и сложности
        reward_modifier = max(0.5, 1.5 - (solution_time / 60))  # Чем быстрее решение, тем выше награда
        reward = int(base_reward * reward_modifier * server_bonus)
        exp_gain = int(difficulty * 20 * reward_modifier)
        
        # Обновляем статистику игрока
        player.money += reward
        player.last_activity = datetime.now().isoformat()
        session.commit()
        
        # Обновляем опыт и получаем новый уровень
        level, experience, level_up = await update_experience(user_id, exp_gain)
        
        return reward, exp_gain, level_up

# Улучшение навыка
async def upgrade_skill(user_id: int, skill_name: str) -> Tuple[bool, int, int]:
    with SessionMaker() as session:
        skill = session.query(Skill).filter(
            Skill.user_id == user_id,
            Skill.skill_name == skill_name
        ).first()
        
        player = session.query(Player).filter(Player.user_id == user_id).first()
        
        if not skill or not player:
            return False, 0, 0
        
        current_level = skill.skill_level
        upgrade_cost = current_level * 200
        
        if player.money >= upgrade_cost:
            skill.skill_level += 1
            player.money -= upgrade_cost
            session.commit()
            
            return True, skill.skill_level, upgrade_cost
        else:
            return False, current_level, upgrade_cost

# Покупка сервера
async def buy_server(user_id: int) -> Tuple[bool, int]:
    with SessionMaker() as session:
        player = session.query(Player).filter(Player.user_id == user_id).first()
        
        if not player:
            return False, 0
        
        server_cost = player.servers * 1000
        
        if player.money >= server_cost:
            player.servers += 1
            player.money -= server_cost
            session.commit()
            
            return True, server_cost
        else:
            return False, server_cost

async def main():
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    # Инициализация диспетчера с хранилищем состояний
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация роутеров
    setup_routers(dp)
    
    # Инициализация базы данных
    await init_db()
    
    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
