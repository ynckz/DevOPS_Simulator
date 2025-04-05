from typing import Tuple
from services.player_service import get_or_create_player, get_player_profile, update_experience, buy_server
from services.incident_service import generate_incident, solve_incident, init_default_incidents
from services.skill_service import upgrade_skill
from services.daily_service import generate_daily_tasks, update_task_progress, claim_task_reward, get_daily_tasks
from services.maintenance_service import repair_server, decrease_server_health
from services.crisis_service import generate_random_crisis, init_default_crises
from models import Skill, Player, SessionMaker

async def upgrade_skill(user_id: int, skill_name: str) -> Tuple[bool, int, int]:
    """Улучшение навыка"""
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