from aiogram import Router, F
from aiogram.types import Message

from models import Player, SessionMaker

# Создаем роутер для рейтинга
rating_router = Router()

@rating_router.message(F.text == '📈 Рейтинг')
async def show_rating(message: Message):
    with SessionMaker() as session:
        # Получаем топ-10 игроков по уровню
        top_players = session.query(
            Player.username, 
            Player.level, 
            Player.experience,
            Player.successful_fixes,
            Player.server_health
        ).order_by(
            Player.level.desc(), 
            Player.experience.desc()
        ).limit(10).all()
        
        if not top_players:
            await message.answer("Пока нет данных для рейтинга.")
            return
        
        # Форматируем список лидеров
        rating_text = "\n\n".join([
            f"{i+1}. *{player[0]}*\n"
            f"Уровень: {player[1]}\n"
            f"Опыт: {player[2]}\n"
            f"Решено инцидентов: {player[3]}\n"
            f"Состояние серверов: {player[4]:.1f}%"
            for i, player in enumerate(top_players)
        ])
        
        await message.answer(
            f"📈 *Рейтинг лучших DevOps-инженеров*\n\n"
            f"{rating_text}\n\n"
            f"Продолжайте улучшать свои навыки, чтобы подняться в рейтинге!",
            parse_mode="Markdown"
        )