"""NadFun-specific interactions for Syndicate agent"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional
from ..core.logger import logger
from ..config.settings import NADFUN_CONTRACTS
from viem import create_public_client, http

class NadFunInteractions:
    def __init__(self, network: str = "testnet"):
        self.network = network
        self.config = NADFUN_CONTRACTS[network]
        self.api_url = self.config["apiUrl"]
        
        # Initialize viem public client
        self.public_client = create_public_client({
            "chain": {
                "id": self.config["chainId"],
                "name": "Monad",
                "nativeCurrency": {"name": "MON", "symbol": "MON", "decimals": 18},
                "rpcUrls": {"default": {"http": [self.config["rpcUrl"]]}},
            },
            "transport": http(self.config["rpcUrl"]),
        })
    
    async def get_token_creation_fee(self) -> int:
        """Get the current token creation fee from the bonding curve router"""
        try:
            # Call feeConfig function on bonding curve router
            result = await self.public_client.read_contract({
                "address": self.config["BONDING_CURVE_ROUTER"],
                "abi": self._get_bonding_curve_router_abi(),
                "functionName": "feeConfig",
            })
            
            # Return deploy fee (first element of the tuple)
            return result[0]
            
        except Exception as e:
            logger.error_blockchain(f"Failed to get token creation fee: {e}")
            return 0
    
    async def upload_image(self, image_ bytes, content_type: str) -> Optional[Dict[str, Any]]:
        """Upload image to NadFun's image service"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/agent/token/image",
                    headers={"Content-Type": content_type},
                    data=image_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info_a2a(f"Image uploaded successfully: {result.get('image_uri')}")
                        return result
                    else:
                        logger.error_blockchain(f"Image upload failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error_blockchain(f"Image upload error: {e}")
            return None
    
    async def upload_metadata(self, image_uri: str, name: str, symbol: str, 
                             description: Optional[str] = None, 
                             website: Optional[str] = None,
                             twitter: Optional[str] = None,
                             telegram: Optional[str] = None) -> Optional[str]:
        """Upload token metadata to NadFun"""
        try:
            metadata_payload = {
                "image_uri": image_uri,
                "name": name,
                "symbol": symbol
            }
            
            if description:
                metadata_payload["description"] = description
            if website:
                metadata_payload["website"] = website
            if twitter:
                metadata_payload["twitter"] = twitter
            if telegram:
                metadata_payload["telegram"] = telegram
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/agent/token/metadata",
                    headers={"Content-Type": "application/json"},
                    json=metadata_payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info_a2a(f"Metadata uploaded successfully: {result.get('metadata_uri')}")
                        return result.get("metadata_uri")
                    else:
                        logger.error_blockchain(f"Metadata upload failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error_blockchain(f"Metadata upload error: {e}")
            return None
    
    async def mine_salt(self, creator_address: str, name: str, symbol: str, metadata_uri: str) -> Optional[Dict[str, Any]]:
        """Mine salt for vanity token address"""
        try:
            payload = {
                "creator": creator_address,
                "name": name,
                "symbol": symbol,
                "metadata_uri": metadata_uri
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/agent/salt",
                    headers={"Content-Type": "application/json"},
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info_a2a(f"Salt mined successfully: {result.get('address')}")
                        return result
                    elif response.status == 408:
                        logger.warn_risk("Salt mining timed out - try again or use random address")
                        return None
                    else:
                        logger.error_blockchain(f"Salt mining failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error_blockchain(f"Salt mining error: {e}")
            return None
    
    async def get_bonding_curve_state(self, token_address: str) -> Optional[Dict[str, Any]]:
        """Get current state of bonding curve for a token"""
        try:
            # This would call the curve contract to get state
            result = await self.public_client.read_contract({
                "address": self.config["CURVE"],
                "abi": self._get_curve_abi(),
                "functionName": "getCurveState",  # Assuming this function exists
                "args": [token_address],
            })
            
            return {
                "virtual_reserves_base": result[0],
                "virtual_reserves_quote": result[1],
                "real_reserves_base": result[2],
                "real_reserves_quote": result[3],
                "k_constant": result[4],
                "target_amount": result[5],
                "graduation_progress": result[6]
            }
            
        except Exception as e:
            logger.error_blockchain(f"Failed to get bonding curve state: {e}")
            return None
    
    async def get_token_progress(self, token_address: str) -> int:
        """Get graduation progress of token (0-10000 = 0-100%)"""
        try:
            # Call getProgress function on LENS contract
            result = await self.public_client.read_contract({
                "address": self.config["LENS"],
                "abi": self._get_lens_abi(),
                "functionName": "getProgress",
                "args": [token_address],
            })
            
            return result
            
        except Exception as e:
            logger.error_blockchain(f"Failed to get token progress: {e}")
            return 0
    
    def _get_bonding_curve_router_abi(self):
        """Get BondingCurveRouter ABI"""
        # This would be imported from abis/router.py
        return []  # Placeholder
    
    def _get_curve_abi(self):
        """Get Curve ABI"""
        # This would be imported from abis/curve.py
        return []  # Placeholder
    
    def _get_lens_abi(self):
        """Get Lens ABI"""
        # This would be imported from abis/lens.py
        return []  # Placeholder
