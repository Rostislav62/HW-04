import asyncio
import websockets

async def listen():
    uri = "ws://127.0.0.1:8000/ws/1"  # Замените `1` на ваш user_id
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Получено сообщение: {message}")

asyncio.run(listen())
