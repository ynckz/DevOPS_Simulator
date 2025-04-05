import random
from datetime import datetime
from typing import Optional, Tuple

from models import Crisis, Player, SessionMaker
from models.skill import Skill
from services.maintenance_service import decrease_server_health

async def init_default_crises():
    """Инициализация базовых кризисов"""
    with SessionMaker() as session:
        # Проверяем, есть ли уже кризисы
        crisis_count = session.query(Crisis).count()
        
        if crisis_count == 0:
            # Заполняем базовые кризисы
            crises = [
                Crisis(
                    name='Отключение электричества', 
                    description='Внезапное отключение электричества привело к сбою в дата-центре.', 
                    severity=3, 
                    server_damage=15,
                    money_loss=300,
                    reputation_loss=5
                ),
                Crisis(
                    name='Массовая хакерская атака', 
                    description='Ваша система подверглась масштабной хакерской атаке.', 
                    severity=4, 
                    server_damage=25,
                    money_loss=600,
                    reputation_loss=10
                ),
                Crisis(
                    name='Сбой в системе охлаждения', 
                    description='Система охлаждения серверов вышла из строя, вызывая перегрев оборудования.', 
                    severity=3, 
                    server_damage=20,
                    money_loss=400,
                    reputation_loss=7
                ),
                Crisis(
                    name='Ошибка в обновлении', 
                    description='Последнее автоматическое обновление содержало критическую ошибку.', 
                    severity=2, 
                    server_damage=10,
                    money_loss=200,
                    reputation_loss=3
                ),
                Crisis(
                    name='Природная катастрофа', 
                    description='Природная катастрофа повлияла на работу ваших серверов.', 
                    severity=5, 
                    server_damage=35,
                    money_loss=800,
                    reputation_loss=15
                )
            ]
            session.add_all(crises)
            session.commit()

async def generate_random_crisis(user_id: int) -> Optional[Tuple[Crisis, bool]]:
    """Генерация случайного кризиса с шансом, зависящим от состояния серверов"""
    with SessionMaker() as session:
        player = session.query(Player).filter(Player.user_id == user_id).first()
        
        if not player:
            return None
        
        # Шанс кризиса зависит от здоровья серверов
        # Чем ниже здоровье, тем выше шанс кризиса
        crisis_chance = (100 - player.server_health) / 100 * 0.3  # максимальный шанс 30%
        
        if random.random() < crisis_chance:
            # Выбираем случайный кризис
            crises = session.query(Crisis).all()
            if not crises:
                return None
                
            # Взвешенный выбор на основе текущего здоровья серверов
            # Чем ниже здоровье, тем выше шанс получить более серьезный кризис
            health_factor = (100 - player.server_health) / 100
            weighted_crises = []
            
            for crisis in crises:
                # Более серьезные кризисы имеют больший вес при низком здоровье
                weight = 1 + (crisis.severity / 5) * health_factor * 2
                weighted_crises.extend([crisis] * int(weight * 10))
            
            selected_crisis = random.choice(weighted_crises)
            
            # С некоторой вероятностью игрок может предотвратить кризис
            # В зависимости от его репутации и навыков
            prevention_chance = player.reputation / 200  # максимальный шанс 50%
            
            # Учитываем навыки игрока
            with SessionMaker() as skill_session:
                monitoring_skill = skill_session.query(Skill).filter(
                    Skill.user_id == user_id,
                    Skill.skill_name == 'Monitoring'
                ).first()
                
                if monitoring_skill:
                    prevention_chance += monitoring_skill.skill_level * 0.05  # +5% за каждый уровень навыка
            
            prevented = random.random() < prevention_chance
            
            if not prevented:
                # Применяем последствия кризиса
                player.money = max(0, player.money - selected_crisis.money_loss)
                player.reputation = max(0, player.reputation - selected_crisis.reputation_loss)
                session.commit()
                
                # Уменьшаем здоровье серверов
                await decrease_server_health(user_id, selected_crisis.server_damage)
            
            return selected_crisis, prevented
        
        return None 