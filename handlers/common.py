from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from utils.keyboards import get_main_keyboard
from services import get_or_create_player

# Создаем роутер для общих команд
common_router = Router()

@common_router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    await get_or_create_player(user_id, username)
    
    await message.answer(
        f"👋 Привет, {username}! Добро пожаловать в Симулятор DevOps-инженера!\n\n"
        f"Твоя задача - решать технические инциденты, улучшать навыки и развивать инфраструктуру.\n\n"
        f"Используй кнопки меню для навигации.", 
        reply_markup=get_main_keyboard()
    )
