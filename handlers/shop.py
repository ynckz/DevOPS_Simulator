from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Text

from services import get_player_profile, buy_server, upgrade_skill
from utils.keyboards import get_shop_keyboard, get_skills_keyboard

# Создаем роутер для магазина
shop_router = Router()

@shop_router.message(Text(text='🛒 Магазин'))
async def show_shop(message: Message):
    user_id = message.from_user.id
    player, _ = await get_player_profile(user_id)
    
    if not player:
        await message.answer("Произошла ошибка. Пожалуйста, перезапустите бота командой /start")
        return
    
    server_cost = player.servers * 1000
    
    await message.answer(
        "🛒 *Магазин DevOps-инженера*\n\n"
        f"У вас сейчас {player.servers} серверов.\n"
        f"Каждый новый сервер увеличивает доход от решения инцидентов на 10%.",
        parse_mode="Markdown",
        reply_markup=get_shop_keyboard(server_cost)
    )

@shop_router.callback_query(F.data == "buy_server")
async def handle_buy_server(call: CallbackQuery):
    user_id = call.from_user.id
    
    success, cost = await buy_server(user_id)
    
    if success:
        player, _ = await get_player_profile(user_id)
        
        if not player:
            await call.answer("Произошла ошибка.")
            return
        
        new_server_cost = player.servers * 1000
        
        await call.message.edit_text(
            "🛒 *Магазин DevOps-инженера*\n\n"
            f"✅ Новый сервер куплен!\n"
            f"У вас сейчас {player.servers} серверов.\n"
            f"Каждый сервер увеличивает доход от решения инцидентов на 10%.",
            parse_mode="Markdown",
            reply_markup=get_shop_keyboard(new_server_cost)
        )
        
        await call.answer("Новый сервер успешно куплен!")
    else:
        await call.answer(f"Недостаточно средств! Необходимо ${cost}")

@shop_router.message(Text(text='📊 Навыки'))
async def show_skills(message: Message):
    user_id = message.from_user.id
    player, skills = await get_player_profile(user_id)
    
    if not player:
        await message.answer("Произошла ошибка. Пожалуйста, перезапустите бота командой /start")
        return
    
    await message.answer(
        "📊 *Ваши навыки DevOps-инженера*\n\n"
        "Выберите навык для улучшения:",
        parse_mode="Markdown",
        reply_markup=get_skills_keyboard(skills)
    )

@shop_router.callback_query(F.data.startswith('upgrade_'))
async def handle_skill_upgrade(call: CallbackQuery):
    user_id = call.from_user.id
    skill_name = call.data.split('_')[1]
    
    success, new_level, cost = await upgrade_skill(user_id, skill_name)
    
    if success:
        await call.answer(f"Навык {skill_name} улучшен до уровня {new_level}!")
        
        # Обновляем меню навыков
        player, skills = await get_player_profile(user_id)
        
        if not player:
            await call.message.edit_text("Произошла ошибка. Пожалуйста, перезапустите бота командой /start")
            return
        
        await call.message.edit_text(
            "📊 *Ваши навыки DevOps-инженера*\n\n"
            "Навык успешно улучшен! Выберите навык для улучшения:",
            parse_mode="Markdown",
            reply_markup=get_skills_keyboard(skills)
        )
    else:
        await call.answer(f"Недостаточно средств! Необходимо ${cost}")
