from fastapi import APIRouter, WebSocket, WebSocketDisconnect


router = APIRouter(tags=["Live Chat"])


class ChatManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, course_id: int, websocket: WebSocket):
        await websocket.accept()

        if course_id not in self.active_connections:
            self.active_connections[course_id] = []

        self.active_connections[course_id].append(websocket)

    def disconnect(self, course_id: int, websocket: WebSocket):
        if course_id in self.active_connections:
            if websocket in self.active_connections[course_id]:
                self.active_connections[course_id].remove(websocket)

            if len(self.active_connections[course_id]) == 0:
                del self.active_connections[course_id]

    async def send_message_to_course(self, course_id: int, message: str):
        if course_id in self.active_connections:
            for connection in self.active_connections[course_id]:
                await connection.send_text(message)


chat_manager = ChatManager()


@router.websocket("/ws/chat/{course_id}")
async def websocket_chat(websocket: WebSocket, course_id: int):
    await chat_manager.connect(course_id, websocket)

    try:
        while True:
            message = await websocket.receive_text()
            full_message = f"Course {course_id}: {message}"
            await chat_manager.send_message_to_course(course_id, full_message)

    except WebSocketDisconnect:
        chat_manager.disconnect(course_id, websocket)