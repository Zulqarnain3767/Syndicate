"""Main orchestrator for Syndicate agent"""

import asyncio
import signal
import sys
from syndicate.rpc_manager import DynamicFailoverManager, RPCEndpoint
from syndicate.blockchain_integration import CostAwareExecutor
from syndicate.nadfun_interactions import NadFunInteractions
from syndicate.wallet_manager import WalletManager
from syndicate.contract_verification import ContractVerifier
from a2a.network_client import A2ANetworkClient
from core.risk_manager import CollaborativeRiskManager
from a2a.message_handler import A2AMessageHandler
from core.logger import logger
from syndicate.wallet_monitor import WalletMonitor
from config.settings import MONAD_RPC_ENDPOINTS, A2A_SERVER_URL, NETWORK, CHAIN_ID

async def main():
    """Main orchestrator for Syndicate"""
    
    logger.success("🚀 Starting Syndicate v1.0.0 - Monad x NadFun Integration")
    logger.info(f"Network: {NETWORK} (Chain ID: {CHAIN_ID})")
    
    # Initialize wallet manager
    wallet_manager = WalletManager()
    wallet_data = wallet_manager.load_wallet()
    wallet_address = wallet_data["address"]
    
    logger.info(f"Using wallet: {wallet_address}")
    
    # Fund wallet if on testnet
    if NETWORK == "testnet":
        logger.info("Checking wallet balance for testnet funding...")
        # Attempt to fund wallet via faucet
        await wallet_manager.fund_wallet_via_faucet(wallet_address)
    
    # Setup RPC endpoints with failover
    rpc_endpoints = [
        RPCEndpoint(url=MONAD_RPC_ENDPOINTS[0], priority=1),
        RPCEndpoint(url=MONAD_RPC_ENDPOINTS[1], priority=2),
        RPCEndpoint(url=MONAD_RPC_ENDPOINTS[2], priority=3)
    ]
    
    rpc_manager = DynamicFailoverManager(rpc_endpoints)
    executor = CostAwareExecutor(rpc_manager, NETWORK)
    nadfun = NadFunInteractions(NETWORK)
    contract_verifier = ContractVerifier()
    wallet_monitor = WalletMonitor(rpc_manager)
    
    # Setup A2A network
    a2a_client = A2ANetworkClient(A2A_SERVER_URL)
    risk_manager = CollaborativeRiskManager()
    message_handler = A2AMessageHandler(a2a_client, risk_manager)
    
    # Connect to A2A network
    await a2a_client.connect()
    await message_handler.start_heartbeat_system()
    
    # Register risk handler
    risk_manager.register_external_advice_handler(
        lambda params: logger.warn_risk(f"Risk parameters adjusted: {params}")
    )
    
    logger.success("✅ All systems initialized successfully")
    logger.info_monad(f"Monad track: Resilient Guardian operational on {NETWORK}")
    logger.info_a2a("A2A track: Social Intelligence online")
    logger.info_monad(f"NadFun integration: Ready for token trading and creation")
    logger.info_monad(f"Wallet: {wallet_manager.get_wallet_address()[:8]}...{wallet_manager.get_wallet_address()[-6:]}")
    
    # Main loop - keep running
    try:
        while True:
            # Perform wallet health checks
            wallet_health = await wallet_monitor.check_health()
            
            # Perform market analysis on NadFun
            # ... (implementation would go here)
            
            # Check for tokens approaching graduation
            # ... (implementation would go here)
            
            await asyncio.sleep(1)  # Main loop interval
            
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        await cleanup(rpc_manager, a2a_client, wallet_manager)

async def cleanup(rpc_manager, a2a_client, wallet_manager):
    """Cleanup resources"""
    logger.info("Performing cleanup...")
    await rpc_manager.close_session()
    await a2a_client.close_connection()
    sys.exit(0)

if __name__ == "__main__":
    # Handle graceful shutdown
    signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(cleanup(None, None, None)))
    asyncio.run(main())
