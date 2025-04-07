import random
from datetime import datetime, timedelta
from typing import List
from models import DailyTask, Player, SessionMaker
from services.player_service import update_experience

async def generate_daily_tasks(user_id: int) -> List[DailyTask]:
    """Генерирует ежедневные задания для игрока"""
    with SessionMaker() as session:
        player = session.query(Player).filter(Player.user_id == user_id).first()
        
        if not player:
            return []
        
        # Удаляем старые задания, если они есть
        session.query(DailyTask).filter(DailyTask.user_id == user_id).delete()
        
        # Генерируем новые задания
        today = datetime.now().date().isoformat()
        
        # Множитель сложности зависит от уровня игрока
        difficulty_multiplier = max(1, player.level / 2)
        
        # Варианты заданий
        task_types = [
            {
                "type": "solve_incidents",
                "description": "Решить инциденты",
                "min_target": 1,
                "max_target": 3 + int(difficulty_multiplier),
                "money_per_unit": 100,
                "exp_per_unit": 20
            },
            {
                "type": "upgrade_skill",
                "description": "Улучшить навыки",
                "min_target": 1,
                "max_target": 2,
                "money_per_unit": 200,
                "exp_per_unit": 30
            },
            {
                "type": "repair_servers", 
                "description": "Восстановить здоровье серверов",
                "min_target": 10,
                "max_target": 30,
                "money_per_unit": 10,
                "exp_per_unit": 2
            }
        ]
        
        # Выбираем 2-3 задания случайно
        num_tasks = random.randint(2, 3)
        selected_tasks = random.sample(task_types, min(num_tasks, len(task_types)))
        
        tasks = []
        for task_info in selected_tasks:
            target_amount = random.randint(task_info["min_target"], task_info["max_target"])
            reward_money = target_amount * task_info["money_per_unit"] * int(difficulty_multiplier)
            reward_exp = target_amount * task_info["exp_per_unit"] * int(difficulty_multiplier)
            
            task = DailyTask(
                user_id=user_id,
                task_type=task_info["type"],
                description=f"{task_info['description']} ({target_amount})",
                target_amount=target_amount,
                reward_money=reward_money,
                reward_exp=reward_exp,
                date_created=today
            )
            
            session.add(task)
            tasks.append(task)
        
        session.commit()
        return tasks

async def update_task_progress(user_id: int, task_type: str, progress: int = 1) -> bool:
    """Обновляет прогресс выполнения задания"""
    with SessionMaker() as session:
        tasks = session.query(DailyTask).filter(
            DailyTask.user_id == user_id,
            DailyTask.task_type == task_type,
            DailyTask.completed == False
        ).all()
        
        if not tasks:
            return False
        
        for task in tasks:
            task.current_amount += progress
            if task.current_amount >= task.target_amount:
                task.completed = True
        
        session.commit()
        return True

async def claim_task_reward(user_id: int, task_id: int) -> tuple:
    """Получить награду за выполненное задание"""
    with SessionMaker() as session:
        task = session.query(DailyTask).filter(
            DailyTask.id == task_id,
            DailyTask.user_id == user_id,
            DailyTask.completed == True
        ).first()
        
        if not task or task.claimed:
            return False, 0, 0
        
        player = session.query(Player).filter(Player.user_id == user_id).first()
        
        if not player:
            return False, 0, 0
        
        # Начисляем награду
        player.money += task.reward_money
        task.claimed = True
        session.commit()
        
        # Начисляем опыт
        level, exp, level_up = await update_experience(user_id, task.reward_exp)
        
        return True, task.reward_money, task.reward_exp

async def get_daily_tasks(user_id: int) -> List[dict]:
    """Получение ежедневных заданий для игрока"""
    with SessionMaker() as session:
        # Проверяем, есть ли задания на сегодня
        today = datetime.now().date().isoformat()
        tasks = session.query(DailyTask).filter(
            DailyTask.user_id == user_id,
            DailyTask.date_created == today
        ).all()
        
        # Если нет заданий на сегодня, создаем новые
        if not tasks:
            tasks = await generate_daily_tasks(user_id)
            # Получаем новые задания из базы
            tasks = session.query(DailyTask).filter(
                DailyTask.user_id == user_id,
                DailyTask.date_created == today
            ).all()
        
        # Копируем данные до закрытия сессии
        return [
            {
                'id': task.id,
                'description': task.description,
                'current_amount': task.current_amount,
                'target_amount': task.target_amount,
                'reward_money': task.reward_money,
                'reward_exp': task.reward_exp,
                'completed': task.completed,
                'claimed': getattr(task, 'claimed', False)
            }
            for task in tasks
        ] 