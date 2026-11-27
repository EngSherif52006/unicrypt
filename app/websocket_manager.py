from collections import defaultdict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active[user_id].add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        self.active[user_id].discard(websocket)
        if not self.active[user_id]:
            self.active.pop(user_id, None)

    def is_online(self, user_id: int) -> bool:
        return bool(self.active.get(user_id))

    async def send_user(self, user_id: int, payload: dict):
        stale = []
        for socket in self.active.get(user_id, set()):
            try:
                await socket.send_json(payload)
            except Exception:
                stale.append(socket)
        for socket in stale:
            self.disconnect(user_id, socket)


manager = ConnectionManager()
