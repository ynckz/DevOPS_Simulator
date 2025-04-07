from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Создание движка SQLAlchemy
engine = create_engine('sqlite:///devops_simulator.db', echo=True)

# Базовый класс для моделей
Base = declarative_base()

# Фабрика сессий
SessionMaker = sessionmaker(bind=engine)

def init_database():
    """Создание всех таблиц"""
    Base.metadata.drop_all(engine)  # Удаляем все существующие таблицы
    Base.metadata.create_all(engine)  # Создаем таблицы заново

def get_session():
    """Получение сессии базы данных"""
    session = SessionMaker()
    try:
        yield session
    finally:
        session.close()