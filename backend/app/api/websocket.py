"""WebSocket endpoint for real-time updates"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio

router = APIRouter()

# Store active connections
active_connections: Dict[int, Set[WebSocket]] = {}

class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, trajectory_id: int):
        """Connect a websocket for a trajectory"""
        await websocket.accept()
        if trajectory_id not in self.active_connections:
            self.active_connections[trajectory_id] = set()
        self.active_connections[trajectory_id].add(websocket)

    def disconnect(self, websocket: WebSocket, trajectory_id: int):
        """Disconnect a websocket"""
        if trajectory_id in self.active_connections:
            self.active_connections[trajectory_id].discard(websocket)
            if not self.active_connections[trajectory_id]:
                del self.active_connections[trajectory_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific websocket"""
        await websocket.send_json(message)

    async def broadcast(self, message: dict, trajectory_id: int):
        """Broadcast message to all clients watching a trajectory"""
        if trajectory_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[trajectory_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)

            # Clean up disconnected clients
            for conn in disconnected:
                self.disconnect(conn, trajectory_id)

manager = ConnectionManager()

@router.websocket("/ws/trajectory/{trajectory_id}")
async def websocket_endpoint(websocket: WebSocket, trajectory_id: int):
    """
    WebSocket endpoint for real-time trajectory updates

    Clients can connect to receive live updates about trajectory execution,
    robot position, and status changes.
    """
    await manager.connect(websocket, trajectory_id)
    try:
        # Send initial connection message
        await manager.send_personal_message({
            "type": "connected",
            "trajectory_id": trajectory_id,
            "message": "Connected to trajectory stream"
        }, websocket)

        while True:
            # Receive messages from client (keep connection alive)
            data = await websocket.receive_text()
            message = json.loads(data)

            # Echo back or handle client messages
            await manager.send_personal_message({
                "type": "ack",
                "received": message
            }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, trajectory_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, trajectory_id)

async def broadcast_update(trajectory_id: int, update: dict):
    """
    Helper function to broadcast updates to all connected clients

    Can be called from other parts of the application to send updates
    """
    await manager.broadcast(update, trajectory_id)
