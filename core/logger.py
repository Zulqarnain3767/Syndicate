"""Professional logging system for Syndicate agent"""

import logging
import sys
from colorama import init, Fore, Style
import json

init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
        'A2A': Fore.BLUE,
        'MONAD': Fore.MAGENTA,
        'RISK': Fore.RED + Style.BRIGHT
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname_colored = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        
        if hasattr(record, 'custom_prefix'):
            prefix = record.custom_prefix
            return f"{prefix}{log_color}{record.getMessage()}{Style.RESET_ALL}"
        else:
            return f"{record.levelname_colored} - {record.getMessage()}"

class ProLogger:
    def __init__(self, name="Syndicate"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = ColoredFormatter('%(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info_a2a(self, message: str):
        """Log A2A-specific messages in blue"""
        self.logger.info(f"{Fore.BLUE}[A2A] {message}")
    
    def info_monad(self, message: str):
        """Log Monad-specific messages in magenta"""
        self.logger.info(f"{Fore.MAGENTA}[MONAD] {message}")
    
    def warn_risk(self, message: str):
        """Log risk-related messages in red with special formatting"""
        self.logger.warning(f"{Fore.RED}[RISK] {message}")
    
    def success(self, message: str):
        """Log success messages in green"""
        self.logger.info(f"{Fore.GREEN}✓ {message}")
    
    def error_blockchain(self, message: str):
        """Log blockchain errors in red"""
        self.logger.error(f"{Fore.RED}[BLOCKCHAIN ERROR] {message}")
    
    def debug_clean(self, message: str):
        """Clean debug logging without spam"""
        if not message.startswith("RPC OK"):
            self.logger.debug(message)

logger = ProLogger()
