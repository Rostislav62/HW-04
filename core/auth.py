# /core/auth.py

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession  # ✅ Добавляем импорт
from db.database import get_db
from models.models import User
from sqlalchemy.future import select  # Добавляем импорт


# Определяем способ передачи токена (в заголовке Authorization)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# 🔐 Настройки JWT
SECRET_KEY = "9qPZSG4mSnGPAKAIWBezewjfJBHDXJGkfIut6zhUZo"  # !!! ЗАМЕНИТЬ на уникальный секретный ключ !!!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Настройки хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 🔹 Хэширование паролей
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# 🔹 Проверка пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# 🔹 Генерация JWT-токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# 🔹 Генерация refresh-токена
def create_refresh_token(data: dict) -> str:
    return create_access_token(data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


# 🔹 Декодирование JWT-токена
def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None





# 🔹 Функция для получения текущего пользователя по токену
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_exception

    email = payload["sub"]

    # 🔹 Исправлено: теперь используем `await db.execute()`
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()

    if user is None:
        raise credentials_exception

    return user
