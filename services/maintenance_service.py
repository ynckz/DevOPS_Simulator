from typing import Tuple

from models import Player, SessionMaker
from services.player_service import update_experience

async def repair_server(user_id: int, repair_percent: int) -> Tuple[bool, float, int]:
    """Ремонт серверов"""
    with SessionMaker() as session:
        player = session.query(Player).filter(Player.user_id == user_id).first()
        
        if not player:
            return False, 0, 0
        
        current_health = player.server_health
        max_repair = 100 - current_health
        
        # Ограничиваем ремонт максимальным значением
        actual_repair = min(max_repair, repair_percent)
        
        # Рассчитываем стоимость ремонта
        repair_cost = int(actual_repair * player.servers * 5)
        
        if player.money >= repair_cost:
            player.server_health = min(100, current_health + actual_repair)
            player.money -= repair_cost
            session.commit()
            
            # Даем небольшое количество опыта за обслуживание
            exp_gain = int(actual_repair / 2)
            if exp_gain > 0:
                await update_experience(user_id, exp_gain)
            
            return True, player.server_health, repair_cost
        else:
            return False, current_health, repair_cost

async def decrease_server_health(user_id: int, amount: float) -> float:
    """Уменьшение здоровья серверов при неудачных решениях или со временем"""
    with SessionMaker() as session:
        player = session.query(Player).filter(Player.user_id == user_id).first()
        
        if not player:
            return 0
        
        player.server_health = max(0, player.server_health - amount)
        session.commit()
        
        return player.server_health