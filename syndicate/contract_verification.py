"""Contract verification for Syndicate agent"""

import json
import subprocess
import aiohttp
from pathlib import Path
from ..core.logger import logger
from ..config.settings import NETWORK, NADFUN_CONTRACTS

class ContractVerifier:
    def __init__(self):
        self.config = NADFUN_CONTRACTS[NETWORK]
        self.chain_id = self.config["chainId"]
    
    async def verify_contract(self, contract_address: str, contract_name: str, 
                            compiler_version: str, standard_json_input: dict,
                            constructor_args: str = None) -> bool:
        """Verify contract using the verification API"""
        try:
            # Prepare verification payload
            payload = {
                "chainId": self.chain_id,
                "contractAddress": contract_address,
                "contractName": contract_name,
                "compilerVersion": f"v{compiler_version}",
                "standardJsonInput": standard_json_input
            }
            
            if constructor_args:
                # Remove 0x prefix if present
                payload["constructorArgs"] = constructor_args.replace("0x", "")
            
            # Call verification API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://agents.devnads.com/v1/verify",
                    headers={"Content-Type": "application/json"},
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.success(f"Contract verified successfully: {contract_address}")
                        logger.info("Verified on all explorers: MonadVision, Socialscan, Monadscan")
                        return True
                    else:
                        logger.error(f"Verification API failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Contract verification error: {e}")
            return False
    
    def get_standard_json_input(self, contract_path: str, contract_name: str) -> dict:
        """Get standard JSON input for verification using forge command"""
        try:
            # Run forge verify-contract to get standard JSON input
            cmd = [
                "forge", "verify-contract",
                contract_path,
                contract_name,
                "--chain", str(self.chain_id),
                "--show-standard-json-input"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            
            if result.returncode == 0:
                return json.loads(result.stdout.strip())
            else:
                logger.error(f"Forge command failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting standard JSON input: {e}")
            return None
    
    def get_compiler_version(self, contract_path: str, contract_name: str) -> str:
        """Extract compiler version from contract artifact"""
        try:
            # Look for the contract artifact
            artifact_path = Path(f"out/{contract_name.split(':')[-1]}.sol/{contract_name.split(':')[-1]}.json")
            
            if artifact_path.exists():
                with open(artifact_path, 'r') as f:
                    artifact = json.load(f)
                
                compiler_version = artifact.get('metadata', {}).get('compiler', {}).get('version', '0.8.27')
                return compiler_version
            else:
                logger.error(f"Artifact not found: {artifact_path}")
                return "0.8.27"  # Default fallback
                
        except Exception as e:
            logger.error(f"Error extracting compiler version: {e}")
            return "0.8.27"
    
    def encode_constructor_args(self, constructor_signature: str, *args) -> str:
        """Encode constructor arguments using cast"""
        try:
            # Use cast to encode constructor arguments
            cmd = ["cast", "abi-encode", constructor_signature] + [str(arg) for arg in args]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                encoded_args = result.stdout.strip()
                return encoded_args.replace("0x", "")  # Remove 0x prefix
            else:
                logger.error(f"Cast encode failed: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"Error encoding constructor args: {e}")
            return ""
