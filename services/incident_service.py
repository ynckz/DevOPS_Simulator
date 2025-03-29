import random
from datetime import datetime
from typing import Optional, Tuple

from models import Incident, Player, SessionMaker
from services.player_service import update_experience

async def generate_incident(user_id: int) -> Optional[Incident]:
    """Генерация случайного инцидента"""
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

async def solve_incident(user_id: int, incident_id: int, solution_time: float) -> Tuple[int, int, bool]:
    """Обработка решения инцидента"""
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

async def init_default_incidents():
    """Инициализация базовых инцидентов"""
    with SessionMaker() as session:
        # Проверяем, есть ли уже инциденты
        incident_count = session.query(Incident).count()
        
        if incident_count == 0:
            # Заполняем базовые инциденты
            incidents = [
                Incident(name='Падение сервера', 
                        description='Сервер внезапно перестал отвечать на запросы', 
                        difficulty=1, reward=100),
                Incident(name='Утечка памяти', 
                        description='В приложении обнаружена утечка памяти', 
                        difficulty=2, reward=200),
                Incident(name='DDoS-атака', 
                        description='Сервера подвергаются DDoS-атаке', 
                        difficulty=3, reward=400),
                Incident(name='Corrupted Database', 
                        description='База данных повреждена и требует восстановления', 
                        difficulty=4, reward=600),
                Incident(name='Нарушение безопасности', 
                        description='Обнаружено нарушение безопасности системы', 
                        difficulty=5, reward=1000)
            ]
            session.add_all(incidents)
            session.commit()
