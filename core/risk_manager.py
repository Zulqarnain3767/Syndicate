"""Collaborative risk management for Syndicate agent"""

import asyncio
from typing import Dict, Any, Callable
from ..core.logger import logger

class CollaborativeRiskManager:
    def __init__(self):
        self.local_risk_params = {
            "max_trade_size": 0.1,
            "volatility_threshold": 0.05,
            "cooldown_period": 30,
            "alert_level": "medium"
        }
        self.external_advice_buffer = []
        self.last_advice_timestamp = 0
        
    def register_external_advice_handler(self, handler_func: Callable):
        """Register function to handle external risk advice"""
        self.external_advice_handler = handler_func
    
    async def process_external_risk_advice(self, advice_ Dict[str, Any]):
        """Process external risk advice and adjust local parameters"""
        try:
            source_agent = advice_data.get("source_agent", "unknown")
            risk_type = advice_data.get("risk_type", "general")
            severity = advice_data.get("severity", "medium")
            details = advice_data.get("details", {})
            
            logger.info_a2a(f"📢 External risk advice from {source_agent}: {risk_type} ({severity})")
            
            self.external_advice_buffer.append({
                "timestamp": asyncio.get_event_loop().time(),
                "source": source_agent,
                "risk_type": risk_type,
                "severity": severity,
                "details": details
            })
            
            if risk_type == "high_volatility":
                if severity == "high":
                    self.local_risk_params["max_trade_size"] *= 0.5
                    self.local_risk_params["alert_level"] = "high"
                    logger.warn_risk("🚨 High volatility detected - reducing trade size by 50%")
                    
                elif severity == "medium":
                    self.local_risk_params["max_trade_size"] *= 0.75
                    logger.info("⚠️ Medium volatility detected - reducing trade size by 25%")
            
            elif risk_type == "market_crash_imminent":
                self.local_risk_params["max_trade_size"] = 0.01
                self.local_risk_params["cooldown_period"] = 300
                logger.critical("🚨 Market crash warning - entering emergency mode")
            
            current_time = asyncio.get_event_loop().time()
            self.external_advice_buffer = [
                advice for advice in self.external_advice_buffer 
                if current_time - advice["timestamp"] < 300
            ]
            
            if hasattr(self, 'external_advice_handler'):
                await self.external_advice_handler(self.local_risk_params)
                
        except Exception as e:
            logger.error(f"Error processing external risk advice: {e}")
    
    def get_adjusted_risk_parameters(self) -> Dict:
        """Get current risk parameters considering external advice"""
        return self.local_risk_params.copy()
