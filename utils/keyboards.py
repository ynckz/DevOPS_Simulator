from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

from models import Skill

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Создать основную клавиатуру"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton(text='🖥 Профиль'),
        KeyboardButton(text='🚨 Инцидент'),
        KeyboardButton(text='📊 Навыки'),
        KeyboardButton(text='🛒 Магазин')
    )
    return markup

def get_skills_keyboard(skills: List[Skill]) -> InlineKeyboardMarkup:
    """Создать клавиатуру навыков"""
    markup = InlineKeyboardMarkup()
    
    for skill in skills:
        upgrade_cost = skill.skill_level * 200
        markup.add(InlineKeyboardButton(
            text=f"{skill.skill_name} (Уровень {skill.skill_level}) - Улучшить за ${upgrade_cost}",
            callback_data=f"upgrade_{skill.skill_name}"
        ))
    
    return markup

def get_shop_keyboard(server_cost: int) -> InlineKeyboardMarkup:
    """Создать клавиатуру магазина"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        text=f"Купить сервер за ${server_cost}", 
        callback_data="buy_server"
    ))
    return markup

def get_incident_solutions_keyboard(incident_id: int) -> InlineKeyboardMarkup:
    """Создать клавиатуру решений инцидента"""
    import random
    
    markup = InlineKeyboardMarkup()
    solutions = [
        ("Перезагрузить", "solution_restart"),
        ("Проверить логи", "solution_logs"),
        ("Исправить код", "solution_code"),
        ("Восстановить данные", "solution_restore"),
        ("Усилить защиту", "solution_security")
    ]
    
    # Добавляем случайные кнопки решений
    random.shuffle(solutions)
    for solution_text, callback_data in solutions[:3]:
        markup.add(InlineKeyboardButton(
            text=solution_text, 
            callback_data=f"{callback_data}_{incident_id}"
        ))
    
    return markup
