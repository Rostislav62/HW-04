# /models/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

# 📌 Модель пользователя
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # Уникальный ID пользователя
    username = Column(String, unique=True, nullable=False)  # Уникальное имя пользователя
    email = Column(String, unique=True, nullable=False)  # Уникальный email
    password_hash = Column(String, nullable=False)  # Захешированный пароль
    refresh_token = Column(String, nullable=True)  # 🔹 Добавили поле `refresh_token`
    created_at = Column(DateTime, default=datetime.utcnow)  # Дата регистрации

    # 📌 Связь: один пользователь -> много сниппетов
    snippets = relationship("Snippet", back_populates="owner")


# 📌 Модель код-сниппета
class Snippet(Base):
    __tablename__ = "snippets"

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, index=True)  # Теперь UUID — основной ключ
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    code = Column(Text, nullable=False)
    language = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    owner = relationship("User", back_populates="snippets")



