from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL

# Создание движка SQLAlchemy
engine = create_engine(DATABASE_URL)

# Базовый класс для моделей
Base = declarative_base()

# Фабрика сессий
SessionMaker = sessionmaker(bind=engine)

def get_session():
    """Получение сессии базы данных"""
    session = SessionMaker()
    try:
        yield session
    finally:
        session.close()