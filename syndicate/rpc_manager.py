"""Dynamic RPC failover manager for Syndicate agent"""

import asyncio
import aiohttp
from typing import List, Optional
from dataclasses import dataclass
import logging
from ..utils.helpers import safe_call_async

@dataclass
class RPCEndpoint:
    url: str
    priority: int
    weight: float = 1.0
    health_score: float = 1.0

class DynamicFailoverManager:
    def __init__(self, rpc_endpoints: List[RPCEndpoint]):
        self.endpoints = sorted(rpc_endpoints, key=lambda x: x.priority)
        self.current_endpoint_idx = 0
        self.session = None
        
    async def get_session(self):
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(limit=50)
            )
        return self.session
    
    async def call_rpc(self, method: str, params: list):
        max_retries = len(self.endpoints)
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                endpoint = self.endpoints[self.current_endpoint_idx]
                session = await self.get_session()
                
                async with session.post(
                    endpoint.url,
                    json={
                        "jsonrpc": "2.0",
                        "method": method,
                        "params": params,
                        "id": 1
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        endpoint.health_score = min(1.0, endpoint.health_score + 0.01)
                        return result
                    elif response.status in [403, 429]:
                        await self.handle_error_response(response.status, endpoint)
                        raise Exception(f"RPC Error {response.status}")
                    else:
                        await self.handle_error_response(response.status, endpoint)
                        raise Exception(f"Unexpected status {response.status}")
                        
            except (aiohttp.ClientConnectorError, aiohttp.DNSLookupError):
                await self.switch_to_backup_endpoint()
                retry_count += 1
                continue
            except Exception as e:
                if "429" in str(e) or "403" in str(e):
                    await self.switch_to_backup_endpoint()
                    retry_count += 1
                    await asyncio.sleep(0.1 * retry_count)
                    continue
                raise
                
        raise Exception("All RPC endpoints failed")
    
    async def handle_error_response(self, status_code: int, endpoint: RPCEndpoint):
        endpoint.health_score = max(0.1, endpoint.health_score - 0.1)
        if status_code in [403, 429]:
            logging.warning(f"Rate limited or forbidden: {endpoint.url}")
            await self.switch_to_backup_endpoint()
    
    async def switch_to_backup_endpoint(self):
        self.current_endpoint_idx = (self.current_endpoint_idx + 1) % len(self.endpoints)
        logging.info(f"Switched to backup RPC endpoint")
    
    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()
