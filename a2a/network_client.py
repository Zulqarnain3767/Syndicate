"""A2A network client for Syndicate agent"""

import websockets
import json
import asyncio
from typing import Callable, Dict
import uuid
from ..core.logger import logger

class A2ANetworkClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.websocket = None
        self.capability_manifest = self._build_capability_manifest()
        self.handlers = {}
        self.is_connected = False
        
    def _build_capability_manifest(self) -> Dict:
        """Build capability manifest for post-handshake"""
        return {
            "agent_id": f"syndicate_{uuid.uuid4().hex[:8]}",
            "capabilities": [
                "liquidity_monitoring",
                "security_alerts",
                "risk_assessment",
                "market_analysis"
            ],
            "version": "1.0.0",
            "metadata": {
                "specialization": "Liquidity Guardian",
                "communication_protocol": "A2A_v2",
                "features": ["real_time_updates", "collaborative_risk"]
            }
        }
    
    async def connect(self):
        """Establish A2A connection with post-handshake capability exchange"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            self.is_connected = True
            
            await self.send_message({
                "type": "capability_manifest",
                "payload": self.capability_manifest,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            logger.success("✓ Connected to A2A network and sent capability manifest")
            
            asyncio.create_task(self.listen_for_messages())
            
        except Exception as e:
            logger.error(f"❌ A2A connection failed: {e}")
            self.is_connected = False
    
    async def send_message(self, message: Dict):
        """Send message to A2A network"""
        if self.websocket and self.is_connected:
            try:
                await self.websocket.send(json.dumps(message))
            except Exception as e:
                logger.error(f"A2A send failed: {e}")
    
    async def listen_for_messages(self):
        """Background task to listen for incoming messages"""
        try:
            async for message in self.websocket:
                await self.handle_incoming_message(json.loads(message))
        except websockets.exceptions.ConnectionClosed:
            logger.warn_risk("⚠️ A2A connection lost")
            self.is_connected = False
            await self.reconnect_with_backoff()
    
    async def handle_incoming_message(self, message: Dict):
        """Handle incoming A2A message"""
        msg_type = message.get("type", "unknown")
        
        if msg_type == "capability_manifest":
            logger.info_a2a(f"Capability manifest received from {message['payload']['agent_id']}")
            
        elif msg_type == "risk_alert":
            logger.info_a2a(f"Risk alert: {message['payload'].get('risk_type', 'N/A')}")
            if hasattr(self, 'risk_callback'):
                await self.risk_callback(message['payload'])
                
        elif msg_type == "heartbeat":
            pass  # Don't log every heartbeat
            
        else:
            logger.info_a2a(f"Message received: {msg_type}")
    
    async def reconnect_with_backoff(self):
        """Reconnect with exponential backoff"""
        backoff_time = 1
        max_backoff = 60
        
        while not self.is_connected:
            try:
                await asyncio.sleep(backoff_time)
                await self.connect()
                if self.is_connected:
                    break
                backoff_time = min(backoff_time * 2, max_backoff)
            except Exception as e:
                logger.error(f"A2A reconnection attempt failed: {e}")
    
    async def close_connection(self):
        """Close A2A connection"""
        if self.websocket:
            await self.websocket.close()
