"""
JARVIS WebSocket Server
Provides real-time communication between web interfaces and JARVIS backend
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime
from typing import Set, Dict, Any
import structlog

# Add this to your existing JARVIS system
logger = structlog.get_logger(__name__)


class JarvisWebSocketServer:
    """WebSocket server for JARVIS web interfaces"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.orchestrator = None  # Will be set by main app
        
    async def register(self, websocket):
        """Register a new client"""
        self.clients.add(websocket)
        logger.info("client_connected", total_clients=len(self.clients))
        await self.send_to_client(websocket, {
            "type": "connection",
            "status": "connected",
            "message": "Connected to JARVIS"
        })
        
    async def unregister(self, websocket):
        """Unregister a client"""
        self.clients.discard(websocket)
        logger.info("client_disconnected", total_clients=len(self.clients))
        
    async def send_to_client(self, websocket, data: Dict[str, Any]):
        """Send data to a specific client"""
        try:
            await websocket.send(json.dumps(data))
        except Exception as e:
            logger.error("send_error", error=str(e))
            
    async def broadcast(self, data: Dict[str, Any]):
        """Broadcast data to all connected clients"""
        if self.clients:
            message = json.dumps(data)
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
            
    async def handle_command(self, websocket, data: Dict[str, Any]):
        """Handle command from web interface"""
        command = data.get("command", "")
        source = data.get("source", "web")
        
        logger.info("web_command_received", command=command, source=source)
        
        # Broadcast activity to all clients
        await self.broadcast({
            "type": "activity",
            "message": f"Executing: {command}",
            "icon": "fa-terminal",
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            # Execute command through orchestrator
            if self.orchestrator:
                result = await self.orchestrator.execute_command(command)
                
                # Send response back to requesting client
                await self.send_to_client(websocket, {
                    "type": "command_response",
                    "command": command,
                    "response": result.get("response", "Command executed"),
                    "success": result.get("success", True),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Broadcast activity
                await self.broadcast({
                    "type": "activity",
                    "message": result.get("response", "Command completed"),
                    "icon": "fa-check-circle",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                await self.send_to_client(websocket, {
                    "type": "command_response",
                    "command": command,
                    "response": "Orchestrator not initialized",
                    "success": False
                })
                
        except Exception as e:
            logger.error("command_execution_error", error=str(e))
            await self.send_to_client(websocket, {
                "type": "command_response",
                "command": command,
                "response": f"Error: {str(e)}",
                "success": False
            })
            
    async def handle_message(self, websocket, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            msg_type = data.get("type", "unknown")
            
            if msg_type == "command":
                await self.handle_command(websocket, data)
            elif msg_type == "ping":
                await self.send_to_client(websocket, {"type": "pong"})
            else:
                logger.warning("unknown_message_type", type=msg_type)
                
        except json.JSONDecodeError:
            logger.error("invalid_json", message=message)
        except Exception as e:
            logger.error("message_handler_error", error=str(e))
            
    async def handler(self, websocket, path):
        """Main WebSocket connection handler"""
        await self.register(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("connection_closed")
        finally:
            await self.unregister(websocket)
            
    async def start(self):
        """Start the WebSocket server"""
        logger.info("websocket_server_starting", host=self.host, port=self.port)
        
        async with websockets.serve(self.handler, self.host, self.port):
            logger.info("websocket_server_running", 
                       url=f"ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever
            
    async def send_system_stats(self, stats: Dict[str, Any]):
        """Send system statistics to all clients"""
        await self.broadcast({
            "type": "system_stats",
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        })
        
    async def send_activity(self, message: str, icon: str = "fa-info-circle"):
        """Send activity update to all clients"""
        await self.broadcast({
            "type": "activity",
            "message": message,
            "icon": icon,
            "timestamp": datetime.now().isoformat()
        })
        
    async def send_memory_update(self, count: int):
        """Send memory count update to all clients"""
        await self.broadcast({
            "type": "memory_update",
            "count": count,
            "timestamp": datetime.now().isoformat()
        })


# Integration with existing JARVIS main.py
def integrate_websocket_server(jarvis_core):
    """
    Add this function to your existing app/main.py
    
    Example usage in JarvisCore class:
    
    class JarvisCore:
        def __init__(self, config_path: str = "app/config.yaml"):
            # ... existing initialization ...
            
            # Add WebSocket server
            self.ws_server = JarvisWebSocketServer(
                host="0.0.0.0",  # Listen on all interfaces
                port=8765
            )
            self.ws_server.orchestrator = self.orchestrator
            
        async def run(self):
            '''Main run loop'''
            # Start WebSocket server in background
            asyncio.create_task(self.ws_server.start())
            
            # ... existing run logic ...
            
        async def send_activity_update(self, message: str, icon: str = "fa-info-circle"):
            '''Send activity updates to web clients'''
            if self.ws_server:
                await self.ws_server.send_activity(message, icon)
    """
    pass


if __name__ == "__main__":
    # Standalone server for testing
    logging.basicConfig(level=logging.INFO)
    server = JarvisWebSocketServer()
    asyncio.run(server.start())
