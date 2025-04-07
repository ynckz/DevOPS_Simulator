from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from services import get_daily_tasks
from services.daily_service import claim_task_reward
from utils.keyboards import get_daily_tasks_keyboard
from models import SessionMaker

# Создаем роутер для заданий
tasks_router = Router()

@tasks_router.message(F.text == '📋 Задания')
async def show_daily_tasks(message: Message):
    user_id = message.from_user.id
    
    # Получаем задания внутри сессии
    with SessionMaker() as session:
        tasks = await get_daily_tasks(user_id)
        
        if not tasks:
            await message.answer("У вас пока нет активных заданий. Попробуйте позже.")
            return
        
        # Формируем текст с заданиями, пока сессия активна
        tasks_text = "\n\n".join([
            f"📌 *{task.description}*\n"
            f"Прогресс: {task.current_amount}/{task.target_amount}\n"
            f"Награда: ${task.reward_money}, ⭐️ {task.reward_exp} опыта\n"
            f"Статус: {'✅ Выполнено' if task.completed else '⏳ В процессе'}"
            for task in tasks
        ])
        
        # Создаем клавиатуру с заданиями
        markup = get_daily_tasks_keyboard(tasks)
        
        await message.answer(
            f"📋 *Ежедневные задания*\n\n"
            f"{tasks_text}\n\n"
            f"Выполняйте задания, чтобы получать дополнительные награды!",
            parse_mode="Markdown",
            reply_markup=markup
        )

@tasks_router.callback_query(F.data.startswith('claim_task_'))
async def handle_claim_task(call: CallbackQuery):
    user_id = call.from_user.id
    task_id = int(call.data.split('_')[-1])
    
    success, money, exp = await claim_task_reward(user_id, task_id)
    
    if success:
        await call.answer(f"Награда получена: ${money} и {exp} опыта!")
        
        # Обновляем список заданий
        with SessionMaker() as session:
            tasks = await get_daily_tasks(user_id)
            
            if not tasks:
                await call.message.edit_text("У вас нет активных заданий.")
                return
            
            tasks_text = "\n\n".join([
                f"📌 *{task['description']}*\n"
                f"Прогресс: {task['current_amount']}/{task['target_amount']}\n"
                f"Награда: ${task['reward_money']}, ⭐️ {task['reward_exp']} опыта\n"
                f"Статус: {'✅ Выполнено' if task['completed'] else '⏳ В процессе'}"
                for task in tasks
            ])
            
            markup = get_daily_tasks_keyboard(tasks)
            
            await call.message.edit_text(
                f"📋 *Ежедневные задания*\n\n"
                f"{tasks_text}\n\n"
                f"Выполняйте задания, чтобы получать дополнительные награды!",
                parse_mode="Markdown",
                reply_markup=markup
            )
    else:
        await call.answer("Не удалось получить награду. Возможно, задание еще не выполнено.") 