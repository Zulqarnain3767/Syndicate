"""Blockchain integration layer for Syndicate agent with NadFun support"""

import asyncio
from decimal import Decimal
from typing import Dict, Any
from .rpc_manager import DynamicFailoverManager
from ..core.logger import logger
from ..config.settings import MAX_TRADE_SIZE_PERCENTAGE, NADFUN_CONTRACTS, NETWORK
from viem import create_public_client, create_wallet_client, http, get_contract
from viem.types import Address
from viem.utils import parse_ether, format_ether

class CostAwareExecutor:
    def __init__(self, rpc_manager: DynamicFailoverManager, network: str = "testnet"):
        self.rpc_manager = rpc_manager
        self.network = network
        self.config = NADFUN_CONTRACTS[network]
        self.gas_price_cache = {}
        
        # Initialize viem clients with proper Monad chain config
        self.public_client = create_public_client({
            "chain": {
                "id": self.config["chainId"],
                "name": "Monad",
                "nativeCurrency": {"name": "MON", "symbol": "MON", "decimals": 18},
                "rpcUrls": {"default": {"http": [self.config["rpcUrl"]]}},
            },
            "transport": http(self.config["rpcUrl"]),
        })
        
    async def estimate_gas_cost(self, transaction_ Dict[str, Any]) -> Decimal:
        """Simulate gas cost before execution"""
        try:
            gas_price_result = await self.rpc_manager.call_rpc(
                "eth_gasPrice", []
            )
            current_gas_price = int(gas_price_result["result"], 16)
            
            gas_estimate_result = await self.rpc_manager.call_rpc(
                "eth_estimateGas", [transaction_data]
            )
            gas_limit = int(gas_estimate_result["result"], 16)
            
            estimated_cost = Decimal(current_gas_price * gas_limit) / Decimal(10**18)
            
            self.gas_price_cache["last_estimate"] = {
                "gas_price": current_gas_price,
                "gas_limit": gas_limit,
                "estimated_cost": estimated_cost
            }
            
            return estimated_cost
            
        except Exception as e:
            logger.error_blockchain(f"Gas estimation failed: {e}")
            return Decimal("0")
    
    async def execute_transaction_with_priority(self, transaction_ Dict[str, Any], priority: str = "normal"):
        """Execute transaction with cost awareness and priority handling"""
        estimated_cost = await self.estimate_gas_cost(transaction_data)
        
        if priority == "high":
            transaction_data["gasPrice"] = hex(int(self.gas_price_cache["last_estimate"]["gas_price"] * 1.2))
        elif priority == "low":
            transaction_data["gasPrice"] = hex(int(self.gas_price_cache["last_estimate"]["gas_price"] * 0.8))
        
        wallet_balance = await self.get_wallet_balance()
        if estimated_cost > wallet_balance * MAX_TRADE_SIZE_PERCENTAGE:
            logger.warning(f"Transaction too expensive: {estimated_cost} vs {wallet_balance}")
            return {"status": "rejected", "reason": "cost_too_high"}
        
        try:
            result = await self.rpc_manager.call_rpc(
                "eth_sendTransaction", [transaction_data]
            )
            logger.success(f"Transaction executed: {result['result']}")
            return {"status": "success", "tx_hash": result["result"]}
        except Exception as e:
            logger.error_blockchain(f"Transaction failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def get_wallet_balance(self) -> Decimal:
        """Get current wallet balance"""
        # Implementation would go here
        return Decimal("10.0")  # Placeholder
    
    # NadFun specific methods
    async def get_token_quote(self, token_address: str, amount_in: int, is_buy: bool) -> tuple[Address, int]:
        """Get price quote for token using NadFun LENS contract"""
        try:
            # Call getAmountOut on LENS contract
            result = await self.public_client.read_contract({
                "address": self.config["LENS"],
                "abi": self._get_lens_abi(),  # Would come from abis/lens.py
                "functionName": "getAmountOut",
                "args": [token_address, amount_in, is_buy],
            })
            
            router_address = result[0]  # First element is router address
            amount_out = result[1]      # Second element is amount out
            
            return router_address, amount_out
            
        except Exception as e:
            logger.error_blockchain(f"Failed to get token quote: {e}")
            return None, 0
    
    async def buy_token(self, token_address: str, amount_in: int, slippage_tolerance: float = 0.005) -> Dict[str, Any]:
        """Execute token purchase on NadFun"""
        try:
            # Get quote first
            router_address, amount_out = await self.get_token_quote(token_address, amount_in, True)
            
            if not router_address:
                return {"status": "failed", "error": "Could not get valid quote"}
            
            # Apply slippage tolerance
            min_amount_out = int(amount_out * (1 - slippage_tolerance))
            deadline = int(asyncio.get_event_loop().time()) + 300  # 5 minutes
            
            # Prepare transaction
            transaction_data = {
                "to": router_address,
                "value": hex(amount_in),
                "data": self._encode_buy_function_call(min_amount_out, token_address, deadline)
            }
            
            return await self.execute_transaction_with_priority(transaction_data)
            
        except Exception as e:
            logger.error_blockchain(f"Token buy failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def check_token_graduation_status(self, token_address: str) -> bool:
        """Check if token has graduated from bonding curve to DEX"""
        try:
            # Call isGraduated function on curve contract
            result = await self.public_client.read_contract({
                "address": self.config["CURVE"],
                "abi": self._get_curve_abi(),  # Would come from abis/curve.py
                "functionName": "isGraduated",
                "args": [token_address],
            })
            
            return result
            
        except Exception as e:
            logger.error_blockchain(f"Failed to check graduation status: {e}")
            return False
    
    def _encode_buy_function_call(self, min_amount_out: int, token_address: str, deadline: int) -> str:
        """Encode buy function call data"""
        # This would use viem's encodeFunctionData utility
        # Implementation would go here
        return "0x00"  # Placeholder
    
    def _get_lens_abi(self):
        """Get LENS contract ABI"""
        # This would be imported from abis/lens.py
        return []  # Placeholder
    
    def _get_curve_abi(self):
        """Get Curve contract ABI"""
        # This would be imported from abis/curve.py
        return []  # Placeholder
