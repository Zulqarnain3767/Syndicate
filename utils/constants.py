"""Constants for Syndicate agent"""

# Transaction priorities
TRANSACTION_PRIORITY = {
    "LOW": 0.8,
    "NORMAL": 1.0,
    "HIGH": 1.2
}

# Risk levels
RISK_LEVELS = {
    "LOW": 0.01,
    "MEDIUM": 0.05,
    "HIGH": 0.1
}

# Network constants
NETWORK_GAS_LIMITS = {
    "testnet": 10000000,
    "mainnet": 10000000
}

# Default timeouts
DEFAULT_TIMEOUT = 30
HEARTBEAT_INTERVAL = 30
RPC_TIMEOUT = 30
