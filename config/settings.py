import os
import logging
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

# Настройки бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в .env файле")

# Настройки базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///devops_simulator.db")

# Настройки логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
