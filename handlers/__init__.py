from aiogram import Dispatcher
from aiogram import Router

from handlers.common import common_router
from handlers.profile import profile_router
from handlers.incidents import incident_router
from handlers.shop import shop_router
from handlers.tasks import tasks_router
from handlers.maintenance import maintenance_router
from handlers.rating import rating_router

def setup_routers(dp: Dispatcher):
    # Создаем главный роутер
    main_router = Router()
    
    # Подключаем все роутеры
    main_router.include_router(common_router)
    main_router.include_router(profile_router)
    main_router.include_router(incident_router)
    main_router.include_router(shop_router)
    main_router.include_router(tasks_router)
    main_router.include_router(maintenance_router)
    main_router.include_router(rating_router)
    
    # Включаем главный роутер в диспетчер
    dp.include_router(main_router)
