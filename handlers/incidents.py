import time
import json
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from services import generate_incident, solve_incident
from utils.keyboards import get_incident_solutions_keyboard
from models import SessionMaker, Player, Skill
from services.maintenance_service import decrease_server_health
from services.daily_service import update_task_progress
from services.crisis_service import generate_random_crisis

# Создаем роутер для инцидентов
incident_router = Router()

# Временное хранилище для данных пользователей
user_data = {}

@incident_router.message(F.text == '🚨 Инцидент')
async def handle_incident(message: Message):
    user_id = message.from_user.id
    
    # Проверяем, не произошел ли кризис
    crisis_result = await generate_random_crisis(user_id)
    
    if crisis_result:
        crisis, prevented = crisis_result
        
        if prevented:
            await message.answer(
                f"⚠️ *ПРЕДОТВРАЩЕНО: {crisis.name}*\n\n"
                f"Благодаря вашей бдительности и хорошему мониторингу, удалось предотвратить кризис:\n"
                f"{crisis.description}\n\n"
                f"Ваши навыки мониторинга и высокая репутация помогли вам заметить и решить проблему заранее!",
                parse_mode="Markdown"
            )
        else:
            severity_stars = "🔴" * crisis.severity + "⚪" * (5 - crisis.severity)
            
            await message.answer(
                f"🚨 *КРИЗИС: {crisis.name}*\n\n"
                f"📝 *Описание:* {crisis.description}\n"
                f"⚠️ *Серьезность:* {severity_stars}\n\n"
                f"*Последствия:*\n"
                f"- Здоровье серверов снизилось на {crisis.server_damage}%\n"
                f"- Потеря ${crisis.money_loss}\n"
                f"- Репутация снизилась на {crisis.reputation_loss} пунктов\n\n"
                f"Вам следует проверить состояние серверов и при необходимости выполнить ремонт.",
                parse_mode="Markdown"
            )
            
            # Даем время пользователю прочитать сообщение о кризисе
            await asyncio.sleep(3)
    
    # Далее генерируем обычный инцидент
    incident = await generate_incident(user_id)
    
    if incident:
        # Сохраняем время начала инцидента для расчёта награды
        user_data[user_id] = {'incident_id': incident.id, 'start_time': time.time()}
        
        stars = "⭐" * incident.difficulty + "☆" * (5 - incident.difficulty)
        
        # Отображаем ограничение по времени, если оно есть
        time_info = ""
        if incident.time_sensitive > 0:
            time_info = f"\n⏱ *Ограничение времени:* {incident.time_sensitive} секунд!"
        
        await message.answer(
            f"🚨 *ИНЦИДЕНТ: {incident.name}*\n\n"
            f"📝 *Описание:* {incident.description}\n"
            f"🔥 *Сложность:* {stars}\n"
            f"💰 *Базовая награда:* ${incident.reward}{time_info}\n\n"
            f"Выберите решение:",
            parse_mode="Markdown",
            reply_markup=get_incident_solutions_keyboard(incident)
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
        
        # Получаем решение из callback_data
        solution_key = call.data.split('_')[1]
        
        # Обрабатываем решение
        success, reward, exp_gain, level_up = await solve_incident(
            user_id, incident_id, solution_key, solution_time
        )
        
        # Обновляем статистику и состояние серверов
        with SessionMaker() as session:
            player = session.query(Player).filter(Player.user_id == user_id).first()
            if player:
                if success:
                    player.successful_fixes += 1
                    # Увеличиваем репутацию при успехе
                    player.reputation = min(100, player.reputation + 2)
                else:
                    player.failed_fixes += 1
                    # Снижаем репутацию при неудаче
                    player.reputation = max(0, player.reputation - 5)
                    
                    # Уменьшаем здоровье серверов при неудаче
                    await decrease_server_health(user_id, 5.0)
                
                session.commit()
        
        # Обновляем прогресс ежедневного задания
        if success:
            await update_task_progress(user_id, "solve_incidents")
        
        if success:
            result_message = f"✅ *Успех!* Инцидент решен за {solution_time:.1f} секунд!\n\n" \
                             f"💰 Получено: ${reward}\n" \
                             f"⭐️ Опыт: +{exp_gain}"
            
            if level_up:
                result_message += f"\n\n🎉 Поздравляем! Вы достигли нового уровня!"
        else:
            result_message = f"❌ *Неудача!* Ваше решение не сработало.\n\n" \
                             f"💰 Потеряно: ${-reward}\n" \
                             f"⭐️ Опыт: +{exp_gain} (учимся на ошибках)\n\n" \
                             f"Состояние серверов снизилось на 5%.\n" \
                             f"Возможно, вам стоит улучшить навыки или выбрать другой подход."
                
        await call.message.edit_text(
            text=call.message.text + f"\n\n{result_message}",
            parse_mode="Markdown"
        )
        
        # Удаляем временные данные пользователя
        del user_data[user_id]
        
        await call.answer()
    else:
        await call.answer("Инцидент не найден. Пожалуйста, сгенерируйте новый.")

# Новый обработчик для просмотра статистики решений
@incident_router.message(F.text == '📊 Статистика')
async def show_stats(message: Message):
    user_id = message.from_user.id
    
    with SessionMaker() as session:
        player = session.query(Player).filter(Player.user_id == user_id).first()
        
        if not player:
            await message.answer("Произошла ошибка. Пожалуйста, перезапустите бота командой /start")
            return
        
        total_incidents = player.successful_fixes + player.failed_fixes
        success_rate = 0 if total_incidents == 0 else (player.successful_fixes / total_incidents) * 100
        
        await message.answer(
            f"📊 *Статистика DevOps-инженера*\n\n"
            f"🖥 *Состояние серверов:* {player.server_health:.1f}%\n"
            f"👨‍💻 *Репутация:* {player.reputation}/100\n"
            f"✅ *Успешно решено инцидентов:* {player.successful_fixes}\n"
            f"❌ *Проваленных инцидентов:* {player.failed_fixes}\n"
            f"📈 *Процент успеха:* {success_rate:.1f}%\n\n"
            f"Продолжайте повышать свои навыки и решать инциденты!",
            parse_mode="Markdown"
        )
