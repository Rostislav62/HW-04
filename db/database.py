# /db/database.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Создание асинхронного движка для SQLite
DATABASE_URL = "sqlite+aiosqlite:///./db/database.db"
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание сессии для работы с БД
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии
async def get_db():
    async with SessionLocal() as session:
        yield session
