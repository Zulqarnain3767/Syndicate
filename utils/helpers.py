"""Helper functions for Syndicate agent"""

import asyncio
from typing import Awaitable, Any

async def safe_call_async(func: Awaitable, default_value: Any = None, retries: int = 3):
    """Safely call async function with retries"""
    for attempt in range(retries):
        try:
            return await func
        except Exception as e:
            if attempt == retries - 1:
                return default_value
            await asyncio.sleep(0.1 * (attempt + 1))

def format_address(address: str) -> str:
    """Format address for display"""
    if len(address) >= 10:
        return f"{address[:6]}...{address[-4:]}"
    return address

def calculate_slippage(base_amount: float, slippage_percentage: float) -> float:
    """Calculate slippage-adjusted amount"""
    return base_amount * (1 - slippage_percentage)

def is_valid_address(address: str) -> bool:
    """Validate EVM address format"""
    return (
        address.startswith("0x") and 
        len(address) == 42 and 
        all(c in "0123456789abcdefABCDEF" for c in address[2:])
    )
