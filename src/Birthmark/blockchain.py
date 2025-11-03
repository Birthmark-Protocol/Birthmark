"""
Blockchain integration for recording and verifying image hashes.

This module provides multiple backend implementations:
- MockBlockchain: For testing and development
- EthereumBlockchain: For Ethereum testnet deployment
- LoopringBlockchain: For production zkRollup deployment (future)

Usage:
    # Development/testing with mock
    blockchain = get_blockchain_interface("mock")
    
    # Ethereum testnet
    blockchain = get_blockchain_interface("ethereum", network="sepolia")
    
    # Loopring zkRollup (future)
    blockchain = get_blockchain_interface("loopring", network="mainnet")
"""

from typing import Dict, Optional, Tuple, List
from datetime import datetime
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import hashlib
import json
import time
from enum import Enum


class BlockchainBackend(Enum):
    """Available blockchain backend implementations."""
    MOCK = "mock"
    ETHEREUM = "ethereum"
    LOOPRING = "loopring"


class BlockchainError(Exception):
    """Base exception for blockchain operations."""
    pass


class TransactionFailedError(BlockchainError):
    """Raised when a transaction fails to submit or confirm."""
    pass


class VerificationError(BlockchainError):
    """Raised when verification fails."""
    pass


@dataclass
class BirthmarkRecord:
    """
    Represents a birthmark record on the blockchain.
    
    Attributes:
        hash: SHA-256 hash of image data
        timestamp: When image was captured (ISO format)
        camera_id: Unique camera identifier (can be anonymized)
        geolocation: Optional GPS coordinates (lat, lon)
        transaction_id: Blockchain transaction ID
        block_number: Block number where transaction was confirmed (optional)
        network: Which blockchain network (testnet/mainnet)
    """
    hash: str
    timestamp: str  # ISO format datetime
    camera_id: str
    geolocation: Optional[Tuple[float, float]] = None
    transaction_id: Optional[str] = None
    block_number: Optional[int] = None
    network: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BirthmarkRecord':
        """Create from dictionary."""
        return cls(**data)


class BlockchainInterface(ABC):
    """
    Abstract base class for blockchain implementations.
    
    All blockchain backends must implement these methods.
    """
    
    @abstractmethod
    def record_hash(
        self,
        image_hash: str,
        timestamp: datetime,
        camera_id: str,
        geolocation: Optional[Tuple[float, float]] = None
    ) -> str:
        """
        Record image hash to blockchain.
        
        Args:
            image_hash: SHA-256 hash of image
            timestamp: Capture timestamp
            camera_id: Camera identifier
            geolocation: Optional (latitude, longitude)
            
        Returns:
            Transaction ID on blockchain
            
        Raises:
            TransactionFailedError: If recording fails
        """
        pass
    
    @abstractmethod
    def verify_hash(
        self,
        image_hash: str
    ) -> Optional[BirthmarkRecord]:
        """
        Verify hash exists on blockchain and retrieve record.
        
        Args:
            image_hash: Hash to look up
            
        Returns:
            BirthmarkRecord if found, None if not found
            
        Raises:
            VerificationError: If lookup fails
        """
        pass
    
    @abstractmethod
    def batch_record_hashes(
        self,
        records: List[Tuple[str, datetime, str, Optional[Tuple[float, float]]]]
    ) -> List[str]:
        """
        Record multiple hashes in a single batch transaction.
        
        Args:
            records: List of (hash, timestamp, camera_id, geolocation) tuples
            
        Returns:
            List of transaction IDs
            
        Raises:
            TransactionFailedError: If batch recording fails
        """
        pass


class MockBlockchain(BlockchainInterface):
    """
    Mock blockchain implementation for testing and development.
    
    Stores records in memory (not persistent). Simulates blockchain
    behavior including transaction IDs and block confirmations.
    
    This is Phase C: Development/Testing implementation.
    """
    
    def __init__(self, network: str = "mock-testnet", simulate_delay: bool = True):
        """
        Initialize mock blockchain.
        
        Args:
            network: Network identifier (for testing different configs)
            simulate_delay: If True, simulates network latency
        """
        self.network = network
        self.simulate_delay = simulate_delay
        self._records: Dict[str, BirthmarkRecord] = {}
        self._transaction_counter = 0
        self._block_counter = 1000
        
    def record_hash(
        self,
        image_hash: str,
        timestamp: datetime,
        camera_id: str,
        geolocation: Optional[Tuple[float, float]] = None
    ) -> str:
        """Record hash to mock blockchain."""
        
        # Simulate network delay
        if self.simulate_delay:
            time.sleep(0.1)  # 100ms simulated latency
        
        # Generate mock transaction ID
        self._transaction_counter += 1
        tx_id = f"mock_tx_{self._transaction_counter:08d}"
        
        # Create record
        record = BirthmarkRecord(
            hash=image_hash,
            timestamp=timestamp.isoformat(),
            camera_id=camera_id,
            geolocation=geolocation,
            transaction_id=tx_id,
            block_number=self._block_counter,
            network=self.network
        )
        
        # Store record
        self._records[image_hash] = record
        
        # Simulate block confirmation
        if self._transaction_counter % 10 == 0:
            self._block_counter += 1
        
        return tx_id
    
    def verify_hash(
        self,
        image_hash: str
    ) -> Optional[BirthmarkRecord]:
        """Verify hash in mock blockchain."""
        
        # Simulate network delay
        if self.simulate_delay:
            time.sleep(0.05)  # 50ms simulated latency
        
        return self._records.get(image_hash)
    
    def batch_record_hashes(
        self,
        records: List[Tuple[str, datetime, str, Optional[Tuple[float, float]]]]
    ) -> List[str]:
        """Record batch of hashes to mock blockchain."""
        
        # Simulate batch transaction delay
        if self.simulate_delay:
            time.sleep(0.2)  # 200ms for batch
        
        tx_ids = []
        for image_hash, timestamp, camera_id, geolocation in records:
            tx_id = self.record_hash(image_hash, timestamp, camera_id, geolocation)
            tx_ids.append(tx_id)
        
        return tx_ids
    
    def get_stats(self) -> Dict:
        """Get mock blockchain statistics (for testing)."""
        return {
            "total_records": len(self._records),
            "current_block": self._block_counter,
            "total_transactions": self._transaction_counter,
            "network": self.network
        }


class EthereumBlockchain(BlockchainInterface):
    """
    Ethereum blockchain implementation using web3.py.
    
    Supports Ethereum testnets (Sepolia, Goerli) and mainnet.
    Uses a simple smart contract to store image hashes.
    
    This is Phase B: Testnet implementation.
    
    Requirements:
        pip install web3
    """
    
    def __init__(
        self,
        network: str = "sepolia",
        provider_url: Optional[str] = None,
        private_key: Optional[str] = None,
        contract_address: Optional[str] = None
    ):
        """
        Initialize Ethereum blockchain interface.
        
        Args:
            network: Network name (sepolia, goerli, mainnet)
            provider_url: RPC provider URL (e.g., Infura, Alchemy)
            private_key: Private key for signing transactions
            contract_address: Deployed contract address
        """
        self.network = network
        self.provider_url = provider_url
        self.private_key = private_key
        self.contract_address = contract_address
        
        # Lazy import to make web3 optional
        try:
            from web3 import Web3
            self.Web3 = Web3
        except ImportError:
            raise ImportError(
                "web3.py is required for Ethereum backend. "
                "Install with: pip install web3"
            )
        
        # Initialize connection
        if provider_url:
            self.w3 = self.Web3(self.Web3.HTTPProvider(provider_url))
            if not self.w3.is_connected():
                raise ConnectionError(f"Failed to connect to Ethereum node at {provider_url}")
        else:
            raise ValueError("provider_url is required for Ethereum backend")
        
        # TODO: Load contract ABI and create contract instance
        # This will be implemented once we deploy the smart contract
        self.contract = None
    
    def record_hash(
        self,
        image_hash: str,
        timestamp: datetime,
        camera_id: str,
        geolocation: Optional[Tuple[float, float]] = None
    ) -> str:
        """
        Record hash to Ethereum blockchain.
        
        TODO: Implement actual transaction submission to smart contract.
        """
        raise NotImplementedError(
            "Ethereum backend is in development. "
            "Use MockBlockchain for testing or help implement this!"
        )
    
    def verify_hash(
        self,
        image_hash: str
    ) -> Optional[BirthmarkRecord]:
        """
        Verify hash on Ethereum blockchain.
        
        TODO: Implement contract query.
        """
        raise NotImplementedError(
            "Ethereum backend is in development. "
            "Use MockBlockchain for testing or help implement this!"
        )
    
    def batch_record_hashes(
        self,
        records: List[Tuple[str, datetime, str, Optional[Tuple[float, float]]]]
    ) -> List[str]:
        """
        Record batch of hashes to Ethereum.
        
        TODO: Implement batch transaction.
        """
        raise NotImplementedError(
            "Ethereum backend is in development. "
            "Use MockBlockchain for testing or help implement this!"
        )


class LoopringBlockchain(BlockchainInterface):
    """
    Loopring zkRollup implementation for production deployment.
    
    Uses Loopring's Layer 2 zkRollup for scalable, low-cost transactions.
    This is the target production backend.
    
    This is Phase A: Production implementation (future).
    
    Requirements:
        pip install loopring-sdk (when available)
    """
    
    def __init__(
        self,
        network: str = "mainnet",
        api_key: Optional[str] = None,
        account_id: Optional[int] = None
    ):
        """
        Initialize Loopring blockchain interface.
        
        Args:
            network: Network (mainnet, testnet)
            api_key: Loopring API key
            account_id: Loopring account ID
        """
        self.network = network
        self.api_key = api_key
        self.account_id = account_id
        
        # TODO: Initialize Loopring SDK connection
        # Will be implemented when we integrate Loopring
    
    def record_hash(
        self,
        image_hash: str,
        timestamp: datetime,
        camera_id: str,
        geolocation: Optional[Tuple[float, float]] = None
    ) -> str:
        """
        Record hash to Loopring zkRollup.
        
        TODO: Implement zkRollup transaction submission.
        """
        raise NotImplementedError(
            "Loopring backend is in development. "
            "This is the future production implementation. "
            "Use MockBlockchain for testing or EthereumBlockchain for testnet."
        )
    
    def verify_hash(
        self,
        image_hash: str
    ) -> Optional[BirthmarkRecord]:
        """
        Verify hash on Loopring zkRollup.
        
        TODO: Implement zkRollup query.
        """
        raise NotImplementedError(
            "Loopring backend is in development. "
            "Use MockBlockchain for testing or EthereumBlockchain for testnet."
        )
    
    def batch_record_hashes(
        self,
        records: List[Tuple[str, datetime, str, Optional[Tuple[float, float]]]]
    ) -> List[str]:
        """
        Record batch of hashes to Loopring zkRollup.
        
        TODO: Implement zkRollup batch transaction.
        This is where zkRollup's efficiency really shines - batching
        thousands of transactions into a single proof.
        """
        raise NotImplementedError(
            "Loopring backend is in development. "
            "Use MockBlockchain for testing or EthereumBlockchain for testnet."
        )


def get_blockchain_interface(
    backend: str = "mock",
    **kwargs
) -> BlockchainInterface:
    """
    Factory function to get the appropriate blockchain interface.
    
    Args:
        backend: Backend type ("mock", "ethereum", "loopring")
        **kwargs: Backend-specific configuration
        
    Returns:
        BlockchainInterface implementation
        
    Example:
        # Mock for testing
        blockchain = get_blockchain_interface("mock")
        
        # Ethereum testnet
        blockchain = get_blockchain_interface(
            "ethereum",
            network="sepolia",
            provider_url="https://sepolia.infura.io/v3/YOUR_KEY"
        )
        
        # Loopring (future)
        blockchain = get_blockchain_interface(
            "loopring",
            network="mainnet",
            api_key="your_key"
        )
    """
    backend = backend.lower()
    
    if backend == "mock":
        return MockBlockchain(**kwargs)
    elif backend == "ethereum":
        return EthereumBlockchain(**kwargs)
    elif backend == "loopring":
        return LoopringBlockchain(**kwargs)
    else:
        raise ValueError(
            f"Unknown backend: {backend}. "
            f"Available: mock, ethereum, loopring"
        )


# Convenience functions for module-level API

def record_to_blockchain(
    image_hash: str,
    timestamp: datetime,
    camera_id: str,
    geolocation: Optional[Tuple[float, float]] = None,
    backend: str = "mock",
    **backend_kwargs
) -> str:
    """
    Record image hash to blockchain (convenience function).
    
    Args:
        image_hash: SHA-256 hash
        timestamp: Capture time
        camera_id: Camera ID
        geolocation: Optional GPS
        backend: Blockchain backend to use
        **backend_kwargs: Backend-specific configuration
        
    Returns:
        Transaction ID
        
    Example:
        tx_id = record_to_blockchain(
            image_hash="abc123...",
            timestamp=datetime.now(),
            camera_id="camera_001",
            backend="mock"
        )
    """
    interface = get_blockchain_interface(backend, **backend_kwargs)
    return interface.record_hash(image_hash, timestamp, camera_id, geolocation)


def verify_from_blockchain(
    image_hash: str,
    backend: str = "mock",
    **backend_kwargs
) -> Optional[BirthmarkRecord]:
    """
    Verify hash on blockchain (convenience function).
    
    Args:
        image_hash: Hash to verify
        backend: Blockchain backend to use
        **backend_kwargs: Backend-specific configuration
        
    Returns:
        BirthmarkRecord if found, None otherwise
        
    Example:
        record = verify_from_blockchain(
            image_hash="abc123...",
            backend="mock"
        )
        if record:
            print(f"Image verified! Captured at {record.timestamp}")
        else:
            print("Image not found on blockchain")
    """
    interface = get_blockchain_interface(backend, **backend_kwargs)
    return interface.verify_hash(image_hash)


def batch_record_to_blockchain(
    records: List[Tuple[str, datetime, str, Optional[Tuple[float, float]]]],
    backend: str = "mock",
    **backend_kwargs
) -> List[str]:
    """
    Record multiple hashes in batch (convenience function).
    
    Args:
        records: List of (hash, timestamp, camera_id, geolocation) tuples
        backend: Blockchain backend to use
        **backend_kwargs: Backend-specific configuration
        
    Returns:
        List of transaction IDs
        
    Example:
        records = [
            ("hash1", datetime.now(), "camera_001", None),
            ("hash2", datetime.now(), "camera_001", (45.5, -122.6)),
            ("hash3", datetime.now(), "camera_002", None)
        ]
        tx_ids = batch_record_to_blockchain(records, backend="mock")
    """
    interface = get_blockchain_interface(backend, **backend_kwargs)
    return interface.batch_record_hashes(records)
