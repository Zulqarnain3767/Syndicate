"""Wallet management for Syndicate agent"""

import os
import json
from pathlib import Path
from viem import create_account, mnemonic_to_account
from viem.utils import to_checksum_address
from ..core.logger import logger
from ..config.settings import NETWORK, FAUCET_API_URL
import aiohttp

class WalletManager:
    def __init__(self):
        self.wallet_path = Path.home() / ".syndicate-wallet"
        self.account = None
        
    def create_new_wallet(self) -> dict:
        """Create a new wallet and persist it securely"""
        try:
            # Create a new account using viem
            from viem.crypto import generate_mnemonic
            from viem.accounts import Account
            
            # Generate a new private key
            from viem.crypto import generate_private_key
            private_key = generate_private_key()
            self.account = Account.from_key(private_key)
            
            # Persist wallet securely
            wallet_data = {
                "private_key": private_key.hex(),
                "address": self.account.address,
                "network": NETWORK,
                "created_at": str(self._get_current_time())
            }
            
            # Write to secure file with restricted permissions
            with open(self.wallet_path, 'w') as f:
                json.dump(wallet_data, f, indent=2)
            os.chmod(self.wallet_path, 0o600)  # Read/write for owner only
            
            logger.success(f"New wallet created and persisted at {self.wallet_path}")
            logger.info(f"Wallet address: {self.account.address}")
            
            return wallet_data
            
        except Exception as e:
            logger.error(f"Failed to create wallet: {e}")
            return None
    
    def load_wallet(self) -> dict:
        """Load existing wallet from persistent storage"""
        try:
            if not self.wallet_path.exists():
                logger.warning("No wallet found, creating new one...")
                return self.create_new_wallet()
            
            with open(self.wallet_path, 'r') as f:
                wallet_data = json.load(f)
            
            # Validate loaded wallet
            if wallet_data.get("network") != NETWORK:
                logger.warn_risk(f"Loaded wallet network mismatch: expected {NETWORK}, got {wallet_data.get('network')}")
            
            # Create account from loaded private key
            from viem.accounts import Account
            self.account = Account.from_key(bytes.fromhex(wallet_data["private_key"].replace("0x", "")))
            
            logger.success(f"Wallet loaded from {self.wallet_path}")
            return wallet_data
            
        except Exception as e:
            logger.error(f"Failed to load wallet: {e}")
            return self.create_new_wallet()  # Create new if loading fails
    
    async def fund_wallet_via_faucet(self, address: str) -> bool:
        """Fund wallet via Monad faucet API"""
        try:
            import asyncio
            
            payload = {
                "chainId": 10143,  # Always use testnet for faucet
                "address": address
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    FAUCET_API_URL,
                    headers={"Content-Type": "application/json"},
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.success(f"Wallet funded via faucet: {result.get('txHash')}")
                        logger.info(f"Funded amount: {result.get('amount')} (1 MON)")
                        return True
                    else:
                        logger.error(f"Faucet funding failed: {response.status}")
                        logger.info("Funding failed, please use official faucet: https://faucet.monad.xyz")
                        return False
                        
        except Exception as e:
            logger.error(f"Faucet funding error: {e}")
            logger.info("Funding failed, please use official faucet: https://faucet.monad.xyz")
            return False
    
    def get_wallet_address(self) -> str:
        """Get current wallet address"""
        if not self.account:
            wallet_data = self.load_wallet()
            if wallet_data:
                return wallet_data["address"]
        return self.account.address if self.account else None
    
    def _get_current_time(self):
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now()
