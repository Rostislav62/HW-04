# /api/auth_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import User
from schemas.schemas import UserCreate, UserResponse
from core.auth import hash_password, verify_password, create_access_token, create_refresh_token
from sqlalchemy.future import select  # Импортируем select
from core.logger import logger  # Импортируем логгер

router = APIRouter()


# 🔹 Регистрация нового пользователя (с логированием)
@router.post("/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == user.email))
    existing_user = result.scalars().first()

    if existing_user:
        logger.warning(f"Попытка регистрации с уже существующим email: {user.email}")
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, password_hash=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(f"Новый пользователь зарегистрирован: {user.email}")
    return new_user


# 🔹 Вход пользователя и выдача токенов (с логированием)
@router.post("/auth/login")
async def login_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == user.email))
    db_user = result.scalars().first()

    if not db_user or not verify_password(user.password, db_user.password_hash):
        logger.warning(f"Ошибка входа: Неверный email или пароль ({user.email})")
        raise HTTPException(status_code=400, detail="Неверный email или пароль")

    access_token = create_access_token({"sub": db_user.email})
    refresh_token = create_refresh_token({"sub": db_user.email})

    db_user.refresh_token = refresh_token
    await db.commit()
    await db.refresh(db_user)

    logger.info(f"Пользователь вошёл: {user.email}")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# 📌 Обновление `access_token` по `refresh_token`
@router.post("/auth/refresh")
async def refresh_access_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.refresh_token == refresh_token))
    db_user = result.scalars().first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Неверный `refresh_token`")

    # 🔹 Генерируем новый `access_token`
    new_access_token = create_access_token({"sub": db_user.email})

    return {"access_token": new_access_token, "token_type": "bearer"}
