from aiogram import Router
from aiogram.types import Message
from aiogram import F
from aiogram.filters import Command

from services import get_player_profile

# Создаем роутер для профиля
profile_router = Router()

@profile_router.message(F.text == '🖥 Профиль')
async def show_profile(message: Message):
    user_id = message.from_user.id
    player, skills = await get_player_profile(user_id)
    
    if player:
        skills_text = "\n".join([f"• {skill.skill_name}: {skill.skill_level} уровень" for skill in skills])
        
        await message.answer(
            f"🖥 *Профиль DevOps-инженера*\n\n"
            f"👤 *Имя:* {player.username}\n"
            f"📊 *Уровень:* {player.level}\n"
            f"⭐️ *Опыт:* {player.experience}/{player.level*100}\n"
            f"💰 *Деньги:* ${player.money}\n"
            f"🖥 *Серверы:* {player.servers}\n\n"
            f"*Навыки:*\n{skills_text}",
            parse_mode="Markdown"
        )
    else:
        await message.answer("Произошла ошибка. Пожалуйста, перезапустите бота командой /start")
