
### `config/settings.py`
```python
"""Configuration settings for Syndicate agent"""

import os
from dotenv import load_dotenv

load_dotenv()

# Monad Configuration
MONAD_RPC_ENDPOINTS = [
    os.getenv("MONAD_RPC_1", "https://testnet-rpc.monad.xyz"),
    os.getenv("MONAD_RPC_2", "https://rpc.monad.xyz"),
    os.getenv("BACKUP_RPC", "https://backup-monad-rpc.example.com")
]

# Network configuration
MONAD_CHAIN_ID = {
    "testnet": 10143,
    "mainnet": 143
}

# Current environment (testnet/mainnet)
NETWORK = os.getenv("MONAD_NETWORK", "testnet")
CHAIN_ID = MONAD_CHAIN_ID[NETWORK]

# NadFun Contract Addresses
NADFUN_CONTRACTS = {
    "testnet": {
        "chainId": 10143,
        "rpcUrl": "https://testnet-rpc.monad.xyz",
        "apiUrl": "https://dev-api.nad.fun",
        "DEX_ROUTER": "0x5D4a4f430cA3B1b2dB86B9cFE48a5316800F5fb2",
        "BONDING_CURVE_ROUTER": "0x865054F0F6A288adaAc30261731361EA7E908003",
        "LENS": "0xB056d79CA5257589692699a46623F901a3BB76f1",
        "CURVE": "0x1228b0dc9481C11D3071E7A924B794CfB038994e",
        "WMON": "0x5a4E0bFDeF88C9032CB4d24338C5EB3d3870BfDd",
        "V3_FACTORY": "0xd0a37cf728CE2902eB8d4F6f2afc76854048253b",
        "CREATOR_TREASURY": "0x24dFf9B68fA36f8400302e2babC3e049eA19459E",
    },
    "mainnet": {
        "chainId": 143,
        "rpcUrl": "https://rpc.monad.xyz",
        "apiUrl": "https://api.nadapp.net",
        "DEX_ROUTER": "0x0B79d71AE99528D1dB24A4148b5f4F865cc2b137",
        "BONDING_CURVE_ROUTER": "0x6F6B8F1a20703309951a5127c45B49b1CD981A22",
        "LENS": "0x7e78A8DE94f21804F7a17F4E8BF9EC2c872187ea",
        "CURVE": "0xA7283d07812a02AFB7C09B60f8896bCEA3F90aCE",
        "WMON": "0x3bd359C1119dA7Da1D913D1C4D2B7c461115433A",
        "V3_FACTORY": "0x6B5F564339DbAD6b780249827f2198a841FEB7F3",
        "CREATOR_TREASURY": "0x42e75B4B96d7000E7Da1e0c729Cec8d2049B9731",
    }
}

# Current environment (testnet/mainnet)
NETWORK = os.getenv("MONAD_NETWORK", "testnet")
CONFIG = NADFUN_CONTRACTS[NETWORK]

# A2A Configuration
A2A_SERVER_URL = os.getenv("A2A_SERVER_URL", "wss://a2a-network-server.example.com")

# Risk Management
MAX_TRADE_SIZE_PERCENTAGE = float(os.getenv("MAX_TRADE_SIZE_PERCENTAGE", "0.1"))
VOLATILITY_THRESHOLD = float(os.getenv("VOLATILITY_THRESHOLD", "0.05"))
COOLDOWN_PERIOD = int(os.getenv("COOLDOWN_PERIOD", "30"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Faucet API
FAUCET_API_URL = "https://agents.devnads.com/v1/faucet"
