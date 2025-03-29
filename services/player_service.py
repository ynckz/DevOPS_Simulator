from datetime import datetime
from typing import Tuple, Optional, List

from models import Player, Skill, SessionMaker

async def get_or_create_player(user_id: int, username: str) -> Player:
    """Получение или создание игрока"""
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

async def get_player_profile(user_id: int) -> Tuple[Optional[Player], List[Skill]]:
    """Получение профиля игрока"""
    with SessionMaker() as session:
        player = session.query(Player).filter(Player.user_id == user_id).first()
        
        if player:
            skills = session.query(Skill).filter(Skill.user_id == user_id).all()
            return player, skills
        return None, []

async def update_experience(user_id: int, exp_gain: int) -> Tuple[int, int, bool]:
    """Обновление опыта и уровня игрока"""
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

async def buy_server(user_id: int) -> Tuple[bool, int]:
    """Покупка сервера"""
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