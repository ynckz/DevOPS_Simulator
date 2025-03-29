import time
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from services import generate_incident, solve_incident
from utils.keyboards import get_incident_solutions_keyboard

# Создаем роутер для инцидентов
incident_router = Router()

# Временное хранилище для данных пользователей
user_data = {}

@incident_router.message(Text(text='🚨 Инцидент'))
async def handle_incident(message: Message):
    user_id = message.from_user.id
    incident = await generate_incident(user_id)
    
    if incident:
        # Сохраняем время начала инцидента для расчёта награды
        user_data[user_id] = {'incident_id': incident.id, 'start_time': time.time()}
        
        stars = "⭐" * incident.difficulty + "☆" * (5 - incident.difficulty)
        
        await message.answer(
            f"🚨 *ИНЦИДЕНТ: {incident.name}*\n\n"
            f"📝 *Описание:* {incident.description}\n"
            f"🔥 *Сложность:* {stars}\n"
            f"💰 *Базовая награда:* ${incident.reward}\n\n"
            f"Выберите решение:",
            parse_mode="Markdown",
            reply_markup=get_incident_solutions_keyboard(incident.id)
        )
    else:
        await message.answer("Сейчас нет активных инцидентов. Попробуйте позже.")

@incident_router.callback_query(F.data.startswith('solution_'))
async def handle_solution(call: CallbackQuery):
    user_id = call.from_user.id
    
    if user_id in user_data:
        incident_data = user_data[user_id]
        solution_time = time.time() - incident_data['start_time']
        incident_id = incident_data['incident_id']
        
        # Получаем ID инцидента из callback_data
        callback_incident_id = int(call.data.split('_')[-1])
        
        if callback_incident_id == incident_id:
            # Правильное решение
            solution_type = call.data.split('_')[1]
            reward, exp_gain, level_up = await solve_incident(user_id, incident_id, solution_time)
            
            result_message = f"✅ Инцидент успешно решен за {solution_time:.1f} секунд!\n\n" \
                             f"💰 Получено: ${reward}\n" \
                             f"⭐️ Опыт: +{exp_gain}"
            
            if level_up:
                result_message += f"\n\n🎉 Поздравляем! Вы достигли нового уровня!"
                
            await call.message.edit_text(
                text=call.message.text + f"\n\n{result_message}",
                parse_mode="Markdown"
            )
            
            # Удаляем временные данные пользователя
            del user_data[user_id]
            
            await call.answer()
        else:
            await call.answer("Этот инцидент уже неактивен.")
    else:
        await call.answer("Инцидент не найден. Пожалуйста, сгенерируйте новый.")
