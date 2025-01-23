# /core/websocket_manager.py

from fastapi import WebSocket
from collections import defaultdict

# 📌 Храним активные WebSocket-соединения (user_id -> list of WebSockets)
active_connections = defaultdict(list)

# 📌 Функция для добавления нового соединения
async def connect(user_id: int, websocket: WebSocket):
    await websocket.accept()
    active_connections[user_id].append(websocket)

# 📌 Функция для удаления соединения при отключении
async def disconnect(user_id: int, websocket: WebSocket):
    if user_id in active_connections:
        active_connections[user_id].remove(websocket)
