import hashlib
import time
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BlockchainCert")

class BlockchainCert:
    """Blockchain certification service for paper verification"""
    
    def __init__(self, storage_path: str = "./storage/blockchain"):
        import os
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        # In a real implementation, this would connect to a blockchain network
        self.chain = []
        self._load_chain()
    
    def certify_paper(self, paper_id: str, version_number: int, content_hash: str) -> Dict[str, Any]:
        """
        Certify paper version on blockchain
        
        Args:
            paper_id: Paper ID
            version_number: Version number
            content_hash: Content hash
            
        Returns:
            Certification metadata
        """
        # Create certification data
        cert_data = {
            "cert_id": f"cert_{paper_id}_{version_number}_{int(time.time())}",
            "paper_id": paper_id,
            "version_number": version_number,
            "content_hash": content_hash,
            "timestamp": datetime.utcnow().isoformat(),
            "blockchain_identifier": f"block_{int(time.time())}_{hashlib.sha256((paper_id + str(version_number)).encode()).hexdigest()[:8]}"
        }
        
        # Add to blockchain (simulated)
        block = self._create_block(cert_data)
        self.chain.append(block)
        self._save_chain()
        
        logger.info(f"Paper certified: {cert_data['cert_id']} for {paper_id} v{version_number}")
        return cert_data
    
    def verify_certification(self, cert_id: str) -> bool:
        """
        Verify paper certification
        
        Args:
            cert_id: Certification ID
            
        Returns:
            True if certification is valid, False otherwise
        """
        # Find certification in blockchain
        for block in self.chain:
            if block.get("cert_data", {}).get("cert_id") == cert_id:
                # Verify block integrity
                if self._verify_block(block):
                    logger.info(f"Certification verified: {cert_id}")
                    return True
        
        logger.warning(f"Certification not found: {cert_id}")
        return False
    
    def get_certification(self, paper_id: str, version_number: int) -> Optional[Dict[str, Any]]:
        """
        Get certification for specific paper version
        
        Args:
            paper_id: Paper ID
            version_number: Version number
            
        Returns:
            Certification data or None if not found
        """
        for block in self.chain:
            cert_data = block.get("cert_data", {})
            if cert_data.get("paper_id") == paper_id and cert_data.get("version_number") == version_number:
                return cert_data
        
        return None
    
    def _create_block(self, cert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create blockchain block
        
        Args:
            cert_data: Certification data
            
        Returns:
            Block data
        """
        previous_hash = self.chain[-1]["hash"] if self.chain else "0" * 64
        
        block = {
            "index": len(self.chain) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "cert_data": cert_data,
            "previous_hash": previous_hash,
            "hash": ""
        }
        
        # Calculate block hash
        block["hash"] = self._calculate_block_hash(block)
        return block
    
    def _calculate_block_hash(self, block: Dict[str, Any]) -> str:
        """
        Calculate block hash
        
        Args:
            block: Block data
            
        Returns:
            Hash value
        """
        block_data = f"{block['index']}|{block['timestamp']}|{block['cert_data']}|{block['previous_hash']}"
        return hashlib.sha256(block_data.encode("utf-8")).hexdigest()
    
    def _verify_block(self, block: Dict[str, Any]) -> bool:
        """
        Verify block integrity
        
        Args:
            block: Block data
            
        Returns:
            True if block is valid, False otherwise
        """
        # Calculate expected hash
        expected_hash = self._calculate_block_hash(block)
        return block["hash"] == expected_hash
    
    def _save_chain(self):
        """
        Save blockchain to storage
        """
        import json
        chain_path = f"{self.storage_path}/blockchain.json"
        
        with open(chain_path, "w", encoding="utf-8") as f:
            json.dump(self.chain, f, indent=2, default=str)
    
    def _load_chain(self):
        """
        Load blockchain from storage
        """
        import json
        import os
        
        chain_path = f"{self.storage_path}/blockchain.json"
        if os.path.exists(chain_path):
            with open(chain_path, "r", encoding="utf-8") as f:
                self.chain = json.load(f)
