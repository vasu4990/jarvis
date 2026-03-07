"""
ESP32 Serial Bridge - Communication protocol implementation
"""

import asyncio
import serial
import json
import structlog
from typing import Callable, Awaitable, Optional
from datetime import datetime

logger = structlog.get_logger(__name__)


class SerialBridge:
    """Manages serial communication with ESP32"""
    
    PROTOCOL_VERSION = "1.0"
    
    def __init__(self, config, event_callback: Callable[[str, dict], Awaitable]):
        self.config = config
        self.event_callback = event_callback
        
        self.port = config.get("mcu.serial_port", "COM3")
        self.baud_rate = config.get("mcu.baud_rate", 115200)
        self.timeout = config.get("mcu.timeout", 1.0)
        self.heartbeat_interval = config.get("mcu.heartbeat_interval", 5)
        
        self.serial_conn: Optional[serial.Serial] = None
        self.running = False
        self.connected = False
        self.last_heartbeat = None
        
    async def start(self):
        """Start serial communication"""
        self.running = True
        
        # Try to connect
        await self.connect()
        
        if not self.connected:
            logger.error("Failed to connect to ESP32")
            return
            
        # Start reader and heartbeat tasks
        reader_task = asyncio.create_task(self._read_loop())
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        await asyncio.gather(reader_task, heartbeat_task)
        
    async def stop(self):
        """Stop serial communication"""
        self.running = False
        
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logger.info("Serial port closed")
            
        self.connected = False
        
    async def connect(self):
        """Establish serial connection"""
        max_attempts = self.config.get("mcu.reconnect_attempts", 3)
        retry_delay = self.config.get("mcu.reconnect_delay", 2)
        
        for attempt in range(1, max_attempts + 1):
            try:
                self.serial_conn = serial.Serial(
                    port=self.port,
                    baudrate=self.baud_rate,
                    timeout=self.timeout
                )
                
                # Wait for ESP32 to initialize
                await asyncio.sleep(2)
                
                # Test connection with ping
                await self.send_command("PING", {})
                
                self.connected = True
                self.last_heartbeat = datetime.now()
                
                logger.info(
                    "Connected to ESP32",
                    port=self.port,
                    baud=self.baud_rate,
                    attempt=attempt
                )
                return
                
            except Exception as e:
                logger.warning(
                    f"Connection attempt {attempt}/{max_attempts} failed",
                    error=str(e)
                )
                
                if attempt < max_attempts:
                    await asyncio.sleep(retry_delay)
                    
        self.connected = False
        
    async def send_command(self, command: str, data: dict):
        """Send command to ESP32"""
        if not self.connected or not self.serial_conn:
            logger.warning("Cannot send - not connected", command=command)
            return
            
        try:
            message = {
                "cmd": command,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
            line = json.dumps(message) + "\n"
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.serial_conn.write,
                line.encode('utf-8')
            )
            
            logger.debug("Sent to ESP32", command=command, data=data)
            
        except Exception as e:
            logger.error("Failed to send command", error=str(e), command=command)
            
    async def _read_loop(self):
        """Continuously read from serial port"""
        while self.running and self.connected:
            try:
                if not self.serial_conn or not self.serial_conn.is_open:
                    break
                    
                # Read line
                line = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.serial_conn.readline
                )
                
                if not line:
                    await asyncio.sleep(0.1)
                    continue
                    
                # Parse message
                try:
                    message = json.loads(line.decode('utf-8').strip())
                    await self._handle_message(message)
                except json.JSONDecodeError:
                    # Try plain text format for debugging
                    text = line.decode('utf-8', errors='ignore').strip()
                    if text:
                        logger.debug("ESP32 raw", text=text)
                        
            except Exception as e:
                logger.error("Read error", error=str(e))
                await asyncio.sleep(1)
                
    async def _handle_message(self, message: dict):
        """Process incoming message from ESP32"""
        msg_type = message.get("type", "")
        
        if msg_type == "EVENT":
            event_name = message.get("event", "")
            event_data = message.get("data", {})
            
            logger.info("ESP32 event", event=event_name, data=event_data)
            
            # Call event callback
            await self.event_callback(event_name, event_data)
            
        elif msg_type == "PONG":
            self.last_heartbeat = datetime.now()
            logger.debug("Heartbeat received")
            
        elif msg_type == "STATUS":
            status = message.get("data", {})
            logger.debug("ESP32 status", status=status)
            
        elif msg_type == "ERROR":
            error = message.get("error", "")
            logger.warning("ESP32 error", error=error)
            
        else:
            logger.debug("Unknown message type", message=message)
            
    async def _heartbeat_loop(self):
        """Send periodic heartbeat pings"""
        while self.running and self.connected:
            await asyncio.sleep(self.heartbeat_interval)
            
            # Check last heartbeat
            if self.last_heartbeat:
                elapsed = (datetime.now() - self.last_heartbeat).total_seconds()
                if elapsed > self.heartbeat_interval * 3:
                    logger.warning("Heartbeat timeout - ESP32 may be disconnected")
                    # Try to reconnect
                    await self.connect()
                    
            # Send ping
            await self.send_command("PING", {})
