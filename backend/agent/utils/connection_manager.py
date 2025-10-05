from fastapi import WebSocket
from typing import List
import logging

logger = logging.getLogger("uvicorn")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket client connected")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info("WebSocket client disconnected")

    async def send_event(self, event_type: str, data: dict):
        """Send event to all connected clients"""
        message = {"type": event_type, "data": data}
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
                logger.info(f"Sent event: {event_type}")
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                
                
manager = ConnectionManager()