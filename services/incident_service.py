import random
import time
from datetime import datetime
from typing import Optional, Tuple, Dict, List

from models import Incident, Player, SessionMaker, Skill
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

async def solve_incident(user_id: int, incident_id: int, solution_key: str, solution_time: float) -> Tuple[bool, int, int, bool]:
    """Обработка решения инцидента с вероятностью успеха"""
    with SessionMaker() as session:
        incident = session.query(Incident).filter(Incident.id == incident_id).first()
        player = session.query(Player).filter(Player.user_id == user_id).first()
        
        if not incident or not player:
            return False, 0, 0, False
        
        # Проверяем, существует ли выбранное решение
        solutions = incident.possible_solutions
        if solution_key not in solutions:
            return False, 0, 0, False
        
        solution = solutions[solution_key]
        difficulty = incident.difficulty
        base_reward = incident.reward
        
        # Проверяем, просрочено ли время для решения (если инцидент ограничен по времени)
        if incident.time_sensitive > 0 and solution_time > incident.time_sensitive:
            success = False
            # Штраф за просрочку
            player.money -= base_reward // 2
            session.commit()
            return success, 0, 0, False
        
        # Получаем уровень навыка, влияющего на решение
        skill_name = solution['skill']
        skill = session.query(Skill).filter(
            Skill.user_id == user_id,
            Skill.skill_name == skill_name
        ).first()
        
        skill_level = skill.skill_level if skill else 1
        
        # Расчет вероятности успеха с учетом уровня навыка
        base_success_rate = solution['success_rate']
        skill_bonus = (skill_level - 1) * 0.05  # Каждый уровень навыка дает +5% к успеху
        final_success_rate = min(0.95, base_success_rate + skill_bonus)  # Максимум 95% шанс
        
        # Определяем успех решения
        success = random.random() < final_success_rate
        
        if success:
            # Бонус от количества серверов
            server_bonus = 1 + (player.servers - 1) * 0.1
            
            # Расчет награды в зависимости от времени решения и сложности
            time_modifier = 1.0
            if incident.time_sensitive > 0:
                time_modifier = max(0.5, 1.5 - (solution_time / incident.time_sensitive))
            
            reward = int(base_reward * time_modifier * server_bonus)
            exp_gain = int(difficulty * 20 * time_modifier)
            
            # Обновляем статистику игрока
            player.money += reward
            player.last_activity = datetime.now().isoformat()
            session.commit()
            
            # Обновляем опыт и получаем новый уровень
            level, experience, level_up = await update_experience(user_id, exp_gain)
            
            return success, reward, exp_gain, level_up
        else:
            # При неудаче игрок теряет часть денег и получает минимальный опыт
            penalty = base_reward // 4
            player.money = max(0, player.money - penalty)
            player.last_activity = datetime.now().isoformat()
            session.commit()
            
            # Даже при неудаче игрок получает небольшой опыт "на ошибках учатся"
            min_exp = difficulty * 5
            level, experience, level_up = await update_experience(user_id, min_exp)
            
            return success, -penalty, min_exp, level_up

async def init_default_incidents():
    """Инициализация базовых инцидентов с вероятностью успеха для разных решений"""
    with SessionMaker() as session:
        # Проверяем, есть ли уже инциденты
        incident_count = session.query(Incident).count()
        
        if incident_count == 0:
            # Заполняем базовые инциденты с вероятностями успеха для разных решений
            incidents = [
                Incident(
                    name='Падение сервера', 
                    description='Сервер внезапно перестал отвечать на запросы', 
                    difficulty=1, 
                    reward=100,
                    possible_solutions={
                        'restart': {'name': 'Перезагрузить сервер', 'success_rate': 0.9, 'skill': 'Linux'},
                        'logs': {'name': 'Проверить логи', 'success_rate': 0.7, 'skill': 'Monitoring'},
                        'config': {'name': 'Проверить конфигурацию', 'success_rate': 0.6, 'skill': 'Linux'},
                        'firewall': {'name': 'Отключить файрвол', 'success_rate': 0.4, 'skill': 'Networking'}
                    },
                    time_sensitive=60
                ),
                Incident(
                    name='Утечка памяти', 
                    description='В приложении обнаружена утечка памяти', 
                    difficulty=2, 
                    reward=200,
                    possible_solutions={
                        'restart': {'name': 'Перезагрузить приложение', 'success_rate': 0.5, 'skill': 'Linux'},
                        'logs': {'name': 'Анализировать логи', 'success_rate': 0.6, 'skill': 'Monitoring'},
                        'code': {'name': 'Исправить код', 'success_rate': 0.8, 'skill': 'Docker'},
                        'profiler': {'name': 'Использовать профайлер', 'success_rate': 0.7, 'skill': 'CI/CD'}
                    }
                ),
                Incident(
                    name='DDoS-атака', 
                    description='Сервера подвергаются DDoS-атаке', 
                    difficulty=3, 
                    reward=400,
                    possible_solutions={
                        'firewall': {'name': 'Настроить файрвол', 'success_rate': 0.7, 'skill': 'Networking'},
                        'cdn': {'name': 'Использовать CDN', 'success_rate': 0.8, 'skill': 'Networking'},
                        'scale': {'name': 'Масштабировать ресурсы', 'success_rate': 0.6, 'skill': 'Docker'},
                        'blacklist': {'name': 'Блокировать IP-адреса', 'success_rate': 0.5, 'skill': 'Linux'}
                    },
                    time_sensitive=45
                ),
                Incident(
                    name='Corrupted Database', 
                    description='База данных повреждена и требует восстановления', 
                    difficulty=4, 
                    reward=600,
                    possible_solutions={
                        'backup': {'name': 'Восстановить из бэкапа', 'success_rate': 0.8, 'skill': 'Docker'},
                        'repair': {'name': 'Запустить восстановление', 'success_rate': 0.6, 'skill': 'Linux'},
                        'replicate': {'name': 'Использовать реплику', 'success_rate': 0.7, 'skill': 'Monitoring'},
                        'export': {'name': 'Экспорт неповрежденных данных', 'success_rate': 0.5, 'skill': 'CI/CD'}
                    }
                ),
                Incident(
                    name='Нарушение безопасности', 
                    description='Обнаружено нарушение безопасности системы', 
                    difficulty=5, 
                    reward=1000,
                    possible_solutions={
                        'audit': {'name': 'Провести аудит', 'success_rate': 0.7, 'skill': 'Linux'},
                        'patch': {'name': 'Установить патчи', 'success_rate': 0.8, 'skill': 'CI/CD'},
                        'isolate': {'name': 'Изолировать систему', 'success_rate': 0.6, 'skill': 'Networking'},
                        'scan': {'name': 'Сканировать на вирусы', 'success_rate': 0.5, 'skill': 'Monitoring'}
                    },
                    time_sensitive=90
                ),
                # Новые инциденты
                Incident(
                    name='Срабатывание мониторинга', 
                    description='Система мониторинга сообщает о высокой нагрузке на CPU', 
                    difficulty=2, 
                    reward=250,
                    possible_solutions={
                        'kill': {'name': 'Завершить проблемные процессы', 'success_rate': 0.7, 'skill': 'Linux'},
                        'scale': {'name': 'Увеличить мощность', 'success_rate': 0.8, 'skill': 'Docker'},
                        'optimize': {'name': 'Оптимизировать код', 'success_rate': 0.6, 'skill': 'CI/CD'},
                        'cron': {'name': 'Проверить cron-задачи', 'success_rate': 0.5, 'skill': 'Linux'}
                    },
                    time_sensitive=30
                ),
                Incident(
                    name='Проблема с DNS', 
                    description='Пользователи не могут получить доступ к сайту из-за проблем с DNS', 
                    difficulty=3, 
                    reward=350,
                    possible_solutions={
                        'refresh': {'name': 'Обновить DNS записи', 'success_rate': 0.8, 'skill': 'Networking'},
                        'provider': {'name': 'Связаться с провайдером', 'success_rate': 0.6, 'skill': 'Networking'},
                        'cache': {'name': 'Очистить DNS кэш', 'success_rate': 0.7, 'skill': 'Linux'},
                        'configure': {'name': 'Изменить DNS конфигурацию', 'success_rate': 0.5, 'skill': 'Docker'}
                    }
                ),
                Incident(
                    name='Сбой в CI/CD пайплайне', 
                    description='Автоматическое развертывание не работает из-за ошибки в пайплайне', 
                    difficulty=4, 
                    reward=450,
                    possible_solutions={
                        'logs': {'name': 'Анализ логов сборки', 'success_rate': 0.7, 'skill': 'CI/CD'},
                        'rollback': {'name': 'Откатить изменения', 'success_rate': 0.8, 'skill': 'CI/CD'},
                        'dependencies': {'name': 'Обновить зависимости', 'success_rate': 0.6, 'skill': 'Docker'},
                        'fix': {'name': 'Исправить скрипты', 'success_rate': 0.7, 'skill': 'Linux'}
                    },
                    time_sensitive=70
                )
            ]
            session.add_all(incidents)
            session.commit()
