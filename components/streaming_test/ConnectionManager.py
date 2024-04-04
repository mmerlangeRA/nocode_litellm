import asyncio

from fastapi import WebSocket
from typing import Union, List, Dict


class ConnectionManager:
    def __init__(self):
        self.__active_connections = dict()

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.__active_connections[user_id] = websocket

    def get_websocket(self, userId: str) -> Union[WebSocket, None]:
        if userId in self.__active_connections:
            return self.__active_connections[userId]

        return None

    async def disconnect(self, userId: str):
        if userId in self.__active_connections:
            websocket = self.get_websocket(userId)
            try:
                # await websocket.close()
                self.__active_connections.pop(userId)
                print(f"websocket closed for {userId}")
            except Exception:
                pass

    async def disconnect_all(self):
        tasks = []
        if self.__active_connections:
            for user_id, websocket in self.__active_connections.items():
                tasks.append(websocket.close())

            results = await asyncio.gather(*tasks, return_exceptions=True)
            exceptions = [res for res in results if isinstance(res, Exception)]
            successful_results = [res for res in results if not isinstance(res, Exception)]

            if exceptions:
                for exception in exceptions:
                    print(f"exception in closing socket: {exception}")

            print(f"closed sockets of {len(successful_results)} clients")

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_json(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def send_messages(self, params: List[Dict]):
        tasks = []
        for param in params:
            user_id = param.get("user_id")
            websocket = self.get_websocket(user_id)
            message = param.get("message")

            if websocket is None:
                continue

            task = websocket.send_text(message)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        exceptions = [res for res in results if isinstance(res, Exception)]
        successful_results = [res for res in results if not isinstance(res, Exception)]

        if exceptions:
            for exception in exceptions:
                print(f"exception in sending message: {exception}")

        print(f"sent messages to {len(successful_results)} clients")

    async def broadcast(self, message: dict):
        for connection in self.__active_connections:
            await connection.send_json(message)