# app/websockets.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.
    """
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept and store a new WebSocket connection.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket connected: %s", websocket.client)

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("WebSocket disconnected: %s", websocket.client)

    async def broadcast(self, message: str) -> None:
        """
        Send a message to all active WebSocket connections.
        If a connection is invalid, remove it from the list.
        """
        # Use a shallow copy to iterate safely.
        for connection in self.active_connections[:]:
            try:
                # If the connection is missing or doesn't have send_text, remove it.
                if connection is None or not hasattr(connection, "send_text"):
                    self.active_connections.remove(connection)
                    continue
                await connection.send_text(message)
            except Exception as e:
                logger.error("Error sending message via websocket: %s", e)
                try:
                    self.active_connections.remove(connection)
                except Exception:
                    pass

# Global instance of the ConnectionManager
manager = ConnectionManager()
