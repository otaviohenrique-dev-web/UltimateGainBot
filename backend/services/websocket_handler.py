from fastapi import WebSocket
import asyncio

class ConnectionManager:
    """Gerencia conexões WebSocket ativas e broadcasting."""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f">>> 🔌 Novo cliente WS conectado. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f">>> 🔌 Cliente WS desconectado. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Envia estado para todos os clients conectados (em paralelo)."""
        if not self.active_connections:
            return
            
        tasks = []
        for connection in self.active_connections:
            tasks.append(asyncio.create_task(self._send_safe(connection, message)))
            
        if tasks:
            await asyncio.gather(*tasks)
            
    async def _send_safe(self, connection: WebSocket, message: dict):
        try:
            await connection.send_json(message)
        except Exception:
            self.disconnect(connection)