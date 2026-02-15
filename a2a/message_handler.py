"""A2A message handler for Syndicate agent"""

import asyncio
import json
from typing import Dict, Any
from .network_client import A2ANetworkClient
from ..core.risk_manager import CollaborativeRiskManager
from ..core.logger import logger

class A2AMessageHandler:
    def __init__(self, network_client: A2ANetworkClient, risk_manager: CollaborativeRiskManager):
        self.network_client = network_client
        self.risk_manager = risk_manager
        self.heartbeat_interval = 30
        self.last_heartbeat = 0
        
    async def start_heartbeat_system(self):
        """Start asynchronous heartbeat in background"""
        asyncio.create_task(self._heartbeat_loop())
        asyncio.create_task(self._monitor_connection_status())
    
    async def _heartbeat_loop(self):
        """Background task for sending heartbeats"""
        while True:
            try:
                if self.network_client.is_connected:
                    heartbeat_msg = {
                        "type": "heartbeat",
                        "agent_id": self.network_client.capability_manifest["agent_id"],
                        "timestamp": asyncio.get_event_loop().time(),
                        "status": "active",
                        "health_metrics": await self._collect_health_metrics()
                    }
                    await self.network_client.send_message(heartbeat_msg)
                    logger.info_a2a(f"Heartbeat sent - active agents: {len(await self._get_active_agents())}")
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_connection_status(self):
        """Monitor and log connection status changes"""
        previous_status = self.network_client.is_connected
        
        while True:
            current_status = self.network_client.is_connected
            
            if current_status != previous_status:
                if current_status:
                    logger.success("A2A connection restored")
                else:
                    logger.warn_risk("A2A connection lost - continuing with local guardian duties")
            
            previous_status = current_status
            await asyncio.sleep(5)
    
    async def handle_incoming_message(self, message: Dict[str, Any]):
        """Handle incoming A2A messages"""
        msg_type = message.get("type", "unknown")
        
        if msg_type == "capability_manifest":
            logger.info_a2a(f"Capability manifest received from {message['payload']['agent_id']}")
            
        elif msg_type == "risk_alert":
            await self.risk_manager.process_external_risk_advice(message["payload"])
            
        elif msg_type == "market_update":
            logger.info_a2a(f"Market update: {message['payload'].get('symbol', 'N/A')}")
            
        elif msg_type == "heartbeat":
            pass
            
        else:
            logger.debug_clean(f"Unknown message type: {msg_type}")
    
    async def _collect_health_metrics(self) -> Dict[str, Any]:
        """Collect health metrics for heartbeat"""
        return {
            "uptime": self._get_uptime(),
            "memory_usage": self._get_memory_usage(),
            "active_connections": 1 if self.network_client.is_connected else 0,
            "last_risk_adjustment": self.risk_manager.last_advice_timestamp
        }
    
    def _get_uptime(self) -> float:
        """Get uptime in seconds"""
        return 0.0  # Placeholder
    
    def _get_memory_usage(self) -> float:
        """Get memory usage percentage"""
        return 0.0  # Placeholder
    
    async def _get_active_agents(self) -> int:
        """Get count of active agents"""
        return 1  # Placeholder
