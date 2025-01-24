# /schemas/schemas.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# 📌 Схема для создания пользователя
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


# 📌 Схема для отображения информации о пользователе (без пароля)
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True  # Позволяет Pydantic корректно работать с SQLAlchemy


# 📌 Схема для создания код-сниппета
class SnippetCreate(BaseModel):
    title: str
    description: Optional[str] = None
    code: str
    language: str


# 📌 Схема для отображения код-сниппета
class SnippetResponse(BaseModel):
    uuid: str  # 🔹 Теперь только UUID
    title: str
    description: Optional[str]
    code: str
    language: str
    created_at: datetime
    updated_at: datetime
    owner_id: int

