# /snippet_api/main.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi
from api.routes import router
from api.auth_routes import router as auth_router
from core.logger import logger  # Логирование событий
from collections import defaultdict
from core.websocket_manager import connect, disconnect  # ✅ Новый импорт


# 🔹 Настройка OAuth2 с передачей токена через заголовок Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# 🔹 Создаём экземпляр FastAPI
app = FastAPI(
    title="Snippet API",
    description="API для работы с код-сниппетами",
    version="1.0",
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
    openapi_url="/openapi.json",
    docs_url="/docs"
)


# 🔹 Функция для корректного определения OpenAPI-схемы
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# 🔹 Подключаем кастомную OpenAPI-схему
app.openapi = custom_openapi

# 🔹 Подключаем маршруты API
app.include_router(router)
app.include_router(auth_router)

# 📌 Храним WebSocket-соединения (для каждого пользователя)
active_connections = defaultdict(list)  # user_id -> list of WebSockets

# 📌 WebSocket для уведомлений о изменениях сниппетов
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await connect(user_id, websocket)  # ✅ Теперь WebSockets управляются централизованно
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await disconnect(user_id, websocket)  # ✅ Корректно удаляем соединение
    logger.info(f"WebSocket-соединение установлено: user_id={user_id}")

    try:
        while True:
            await websocket.receive_text()  # Ждём сообщения (но мы только отправляем)
    except WebSocketDisconnect:
        active_connections[user_id].remove(websocket)
        logger.info(f"WebSocket-соединение закрыто: user_id={user_id}")

# 🔹 Запуск сервера Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
