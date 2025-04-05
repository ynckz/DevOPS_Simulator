from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from services import get_player_profile, repair_server
from utils.keyboards import get_maintenance_keyboard
from services.daily_service import update_task_progress

# Создаем роутер для обслуживания
maintenance_router = Router()

@maintenance_router.message(F.text == '🔧 Обслуживание')
async def show_maintenance(message: Message):
    user_id = message.from_user.id
    player, _ = await get_player_profile(user_id)
    
    if not player:
        await message.answer("Произошла ошибка. Пожалуйста, перезапустите бота командой /start")
        return
    
    server_health = player.server_health
    health_status = "🟢 Отлично" if server_health > 90 else \
                   "🟡 Хорошо" if server_health > 70 else \
                   "🟠 Удовлетворительно" if server_health > 50 else \
                   "🔴 Критически"
    
    repair_cost = int((100 - server_health) * player.servers * 5)
    
    await message.answer(
        f"🔧 *Обслуживание серверов*\n\n"
        f"Текущее состояние: {health_status} ({server_health:.1f}%)\n"
        f"Количество серверов: {player.servers}\n\n"
        f"Стоимость полного ремонта: ${repair_cost}\n\n"
        f"Низкое здоровье серверов увеличивает вероятность сбоев и снижает\n"
        f"эффективность решения инцидентов.",
        parse_mode="Markdown",
        reply_markup=get_maintenance_keyboard(repair_cost)
    )

@maintenance_router.callback_query(F.data.startswith('repair_'))
async def handle_repair(call: CallbackQuery):
    user_id = call.from_user.id
    repair_amount = int(call.data.split('_')[1])  # repair_100, repair_50, repair_25
    
    success, new_health, cost = await repair_server(user_id, repair_amount)
    
    if success:
        # Обновляем прогресс ежедневного задания
        await update_task_progress(user_id, "repair_servers", repair_amount)
        
        health_status = "🟢 Отлично" if new_health > 90 else \
                       "🟡 Хорошо" if new_health > 70 else \
                       "🟠 Удовлетворительно" if new_health > 50 else \
                       "🔴 Критически"
        
        player, _ = await get_player_profile(user_id)
        repair_cost = int((100 - new_health) * player.servers * 5)
        
        await call.message.edit_text(
            f"🔧 *Обслуживание серверов*\n\n"
            f"✅ Ремонт выполнен успешно!\n"
            f"Потрачено: ${cost}\n\n"
            f"Текущее состояние: {health_status} ({new_health:.1f}%)\n"
            f"Количество серверов: {player.servers}\n\n"
            f"Стоимость полного ремонта: ${repair_cost}",
            parse_mode="Markdown",
            reply_markup=get_maintenance_keyboard(repair_cost)
        )
        
        await call.answer("Ремонт выполнен успешно!")
    else:
        await call.answer(f"Недостаточно средств! Необходимо ${cost}") 