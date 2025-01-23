# /api/routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import User, Snippet
from schemas.schemas import UserCreate, UserResponse, SnippetCreate, SnippetResponse
from core.auth import get_current_user  # Импортируем защиту JWT
from sqlalchemy.future import select  # Импортируем select
from core.logger import logger  # Импортируем логгер
from core.websocket_manager import active_connections  # ✅ WebSockets импортируются
from datetime import datetime  # ✅ Добавили импорт datetime
from typing import List, Optional
from fastapi import Query


router = APIRouter()


# 📌 Регистрация нового пользователя
@router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email уже используется")

    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=user.password  # !!! Позже заменим на хеширование пароля !!!
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/snippets/", response_model=SnippetResponse)
async def create_snippet(snippet: SnippetCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_snippet = Snippet(**snippet.dict(), owner_id=current_user.id)
    db.add(new_snippet)
    await db.commit()
    await db.refresh(new_snippet)

    logger.info(f"Сниппет создан пользователем {current_user.email}: {new_snippet.title}")
    return new_snippet



# 📌 Обновление код-сниппета (добавили WebSockets)
@router.put("/snippets/{snippet_id}", response_model=SnippetResponse)
async def update_snippet(
    snippet_id: int,
    updated_snippet: SnippetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Snippet).filter(Snippet.id == snippet_id))
    snippet = result.scalars().first()

    if not snippet:
        raise HTTPException(status_code=404, detail="Сниппет не найден")

    if snippet.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    snippet.title = updated_snippet.title
    snippet.description = updated_snippet.description
    snippet.code = updated_snippet.code
    snippet.language = updated_snippet.language
    snippet.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(snippet)

    # 🔹 Уведомляем владельца о том, что его сниппет обновлён
    if snippet.owner_id in active_connections:
        for connection in active_connections[snippet.owner_id]:
            await connection.send_text(f"Ваш сниппет '{snippet.title}' был обновлён!")

    logger.info(f"Сниппет обновлён пользователем {current_user.email}: {snippet.title}")
    return snippet


# 📌 Удаление код-сниппета (только владелец может удалить) с WebSocket-уведомлением
@router.delete("/snippets/{snippet_id}")
async def delete_snippet(
    snippet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Snippet).filter(Snippet.id == snippet_id))
    snippet = result.scalars().first()

    if not snippet:
        raise HTTPException(status_code=404, detail="Сниппет не найден")

    if snippet.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    db.delete(snippet)
    await db.commit()

    # 🔹 Уведомляем владельца о том, что его сниппет удалён
    if snippet.owner_id in active_connections:
        for connection in active_connections[snippet.owner_id]:
            await connection.send_text(f"Ваш сниппет '{snippet.title}' был удалён!")

    logger.info(f"Сниппет удалён пользователем {current_user.email}: {snippet.title}")
    return {"message": "Сниппет удалён"}



@router.get("/snippets/", response_model=List[SnippetResponse])
async def get_snippets(
    db: AsyncSession = Depends(get_db),
    language: Optional[str] = Query(None, description="Фильтр по языку"),
    owner_id: Optional[int] = Query(None, description="Фильтр по владельцу")
):
    query = select(Snippet)

    if language:
        query = query.filter(Snippet.language == language)  # 🔹 Фильтр по языку
    if owner_id:
        query = query.filter(Snippet.owner_id == owner_id)  # 🔹 Фильтр по владельцу

    result = await db.execute(query)
    snippets = result.scalars().all()
    return snippets
