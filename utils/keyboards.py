from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

from models import Skill

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Создать основную клавиатуру с новыми кнопками"""
    keyboard = [
        [
            KeyboardButton(text='🖥 Профиль'),
            KeyboardButton(text='🚨 Инцидент')
        ],
        [
            KeyboardButton(text='📊 Навыки'),
            KeyboardButton(text='🛒 Магазин')
        ],
        [
            KeyboardButton(text='📋 Задания'),
            KeyboardButton(text='📊 Статистика')
        ],
        [
            KeyboardButton(text='🔧 Обслуживание'),
            KeyboardButton(text='📈 Рейтинг')
        ]
    ]
    
    markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    return markup

def get_skills_keyboard(skills: List[Skill]) -> InlineKeyboardMarkup:
    """Создать клавиатуру навыков"""
    keyboard = []
    
    for skill in skills:
        upgrade_cost = skill.skill_level * 200
        keyboard.append([
            InlineKeyboardButton(
                text=f"{skill.skill_name} (Уровень {skill.skill_level}) - Улучшить за ${upgrade_cost}",
                callback_data=f"upgrade_{skill.skill_name}"
            )
        ])
    
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup

def get_shop_keyboard(server_cost: int) -> InlineKeyboardMarkup:
    """Создать клавиатуру магазина"""
    keyboard = [[
        InlineKeyboardButton(
            text=f"Купить сервер за ${server_cost}", 
            callback_data="buy_server"
        )
    ]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup

def get_incident_solutions_keyboard(incident) -> InlineKeyboardMarkup:
    """Создать клавиатуру решений инцидента на основе возможных решений"""
    keyboard = []
    
    # Получаем список решений из модели инцидента
    solutions = incident.possible_solutions
    
    # Создаем кнопки для каждого возможного решения
    for key, solution in solutions.items():
        keyboard.append([
            InlineKeyboardButton(
                text=solution['name'], 
                callback_data=f"solution_{key}"
            )
        ])
    
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup

def get_daily_tasks_keyboard(tasks) -> InlineKeyboardMarkup:
    """Создать клавиатуру для заданий"""
    keyboard = []
    
    for task in tasks:
        if task.completed and not task.claimed:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"Получить награду за '{task.description}'", 
                    callback_data=f"claim_task_{task.id}"
                )
            ])
    
    # Добавляем кнопку обновления
    keyboard.append([
        InlineKeyboardButton(
            text="🔄 Обновить задания",
            callback_data="refresh_tasks"
        )
    ])
    
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup

def get_maintenance_keyboard(repair_cost: int) -> InlineKeyboardMarkup:
    """Создать клавиатуру для обслуживания серверов"""
    keyboard = []
    
    # Добавляем кнопки с разными вариантами ремонта
    repair_options = [
        ("🔧 Полный ремонт", "repair_100"),
        ("🔧 Средний ремонт (50%)", "repair_50"),
        ("🔧 Минимальный ремонт (25%)", "repair_25")
    ]
    
    for text, callback in repair_options:
        cost = repair_cost
        if callback == "repair_50":
            cost = repair_cost // 2
        elif callback == "repair_25":
            cost = repair_cost // 4
            
        keyboard.append([
            InlineKeyboardButton(
                text=f"{text} - ${cost}", 
                callback_data=callback
            )
        ])
    
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup
