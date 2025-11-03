# Blockchain Module Implementation Guide

## Overview

The blockchain module provides three implementation phases following the **C→B→A** progression:

- **Phase C: Mock** - Development and testing (✅ Implemented)
- **Phase B: Ethereum** - Testnet deployment (🚧 In Progress)
- **Phase A: Loopring** - Production zkRollup (⏳ Planned)

This approach lets us build and test the entire system quickly while having a clear path to production.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                       │
│  (Camera apps, verification clients, web interfaces)    │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Blockchain Interface (Abstract)             │
│    record_hash() │ verify_hash() │ batch_record()       │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│     Mock     │  │   Ethereum   │  │   Loopring   │
│  Blockchain  │  │  Blockchain  │  │  Blockchain  │
│              │  │              │  │              │
│   (Testing)  │  │  (Testnet)   │  │ (Production) │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Current Status

### ✅ Phase C: Mock Implementation (COMPLETE)

The `MockBlockchain` class is fully implemented and tested. It provides:

- **In-memory storage** - Records stored in Python dictionary
- **Transaction simulation** - Generates realistic transaction IDs
- **Block confirmation** - Simulates block progression
- **Network latency** - Optional delay simulation for realistic testing
- **Full API coverage** - All interface methods implemented

**Usage Example:**

```python
from blockchain import MockBlockchain
from datetime import datetime

# Initialize
blockchain = MockBlockchain(simulate_delay=False)

# Record a hash
tx_id = blockchain.record_hash(
    image_hash="abc123...",
    timestamp=datetime.now(),
    camera_id="camera_001",
    geolocation=(45.5231, -122.6765)
)

# Verify a hash
record = blockchain.verify_hash("abc123...")
if record:
    print(f"Verified! Camera: {record.camera_id}")
```

**Testing:**

```bash
# Run tests
python -m pytest test_blockchain.py -v

# Run integration example
python test_blockchain.py
```

### 🚧 Phase B: Ethereum Implementation (IN PROGRESS)

The `EthereumBlockchain` class has the basic structure but needs implementation:

#### What's Done:
- Class structure and initialization
- web3.py integration setup
- Connection management
- Error handling framework

#### What's Needed:

**1. Smart Contract Development**

Create a Solidity contract to store birthmark records:

```solidity
// contracts/BirthmarkRegistry.sol
pragma solidity ^0.8.0;

contract BirthmarkRegistry {
    struct BirthmarkRecord {
        bytes32 imageHash;
        uint256 timestamp;
        bytes32 cameraId;
        int256 latitude;   // Scaled by 1e6 for precision
        int256 longitude;  // Scaled by 1e6 for precision
        bool hasGeolocation;
    }
    
    mapping(bytes32 => BirthmarkRecord) public records;
    mapping(bytes32 => bool) public exists;
    
    event HashRecorded(
        bytes32 indexed imageHash,
        uint256 timestamp,
        bytes32 cameraId
    );
    
    function recordHash(
        bytes32 imageHash,
        uint256 timestamp,
        bytes32 cameraId,
        int256 latitude,
        int256 longitude,
        bool hasGeolocation
    ) public returns (bool) {
        require(!exists[imageHash], "Hash already recorded");
        
        records[imageHash] = BirthmarkRecord({
            imageHash: imageHash,
            timestamp: timestamp,
            cameraId: cameraId,
            latitude: latitude,
            longitude: longitude,
            hasGeolocation: hasGeolocation
        });
        
        exists[imageHash] = true;
        
        emit HashRecorded(imageHash, timestamp, cameraId);
        return true;
    }
    
    function verifyHash(bytes32 imageHash) 
        public 
        view 
        returns (
            bool found,
            uint256 timestamp,
            bytes32 cameraId,
            int256 latitude,
            int256 longitude,
            bool hasGeolocation
        ) 
    {
        if (!exists[imageHash]) {
            return (false, 0, bytes32(0), 0, 0, false);
        }
        
        BirthmarkRecord memory record = records[imageHash];
        return (
            true,
            record.timestamp,
            record.cameraId,
            record.latitude,
            record.longitude,
            record.hasGeolocation
        );
    }
    
    function batchRecordHashes(
        bytes32[] memory imageHashes,
        uint256[] memory timestamps,
        bytes32[] memory cameraIds,
        int256[] memory latitudes,
        int256[] memory longitudes,
        bool[] memory hasGeolocations
    ) public returns (bool) {
        require(
            imageHashes.length == timestamps.length &&
            timestamps.length == cameraIds.length &&
            cameraIds.length == latitudes.length &&
            latitudes.length == longitudes.length &&
            longitudes.length == hasGeolocations.length,
            "Array lengths must match"
        );
        
        for (uint i = 0; i < imageHashes.length; i++) {
            recordHash(
                imageHashes[i],
                timestamps[i],
                cameraIds[i],
                latitudes[i],
                longitudes[i],
                hasGeolocations[i]
            );
        }
        
        return true;
    }
}
```

**2. Contract Deployment**

Deploy to Sepolia testnet:

```bash
# Install dependencies
npm install --save-dev hardhat @nomiclabs/hardhat-ethers ethers

# Create deployment script
npx hardhat run scripts/deploy.js --network sepolia
```

**3. Python Implementation**

Complete the `EthereumBlockchain` class:

```python
def record_hash(
    self,
    image_hash: str,
    timestamp: datetime,
    camera_id: str,
    geolocation: Optional[Tuple[float, float]] = None
) -> str:
    """Record hash to Ethereum."""
    
    # Convert hash to bytes32
    hash_bytes = self.w3.to_bytes(hexstr=image_hash)
    
    # Convert camera_id to bytes32
    camera_bytes = self.w3.to_bytes(text=camera_id[:32])
    
    # Convert timestamp to Unix timestamp
    timestamp_int = int(timestamp.timestamp())
    
    # Handle geolocation
    if geolocation:
        lat_scaled = int(geolocation[0] * 1_000_000)
        lon_scaled = int(geolocation[1] * 1_000_000)
        has_geo = True
    else:
        lat_scaled = 0
        lon_scaled = 0
        has_geo = False
    
    # Build transaction
    tx = self.contract.functions.recordHash(
        hash_bytes,
        timestamp_int,
        camera_bytes,
        lat_scaled,
        lon_scaled,
        has_geo
    ).build_transaction({
        'from': self.account.address,
        'nonce': self.w3.eth.get_transaction_count(self.account.address),
        'gas': 200000,
        'gasPrice': self.w3.eth.gas_price
    })
    
    # Sign and send
    signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
    tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    # Wait for confirmation
    receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return tx_hash.hex()
```

**4. Setup Requirements**

- Infura or Alchemy API key for Sepolia access
- Testnet ETH from Sepolia faucet
- Deploy contract and get contract address
- Update `EthereumBlockchain.__init__()` with ABI

**5. Testing on Testnet**

```python
# Test Ethereum implementation
from blockchain import get_blockchain_interface
from datetime import datetime

blockchain = get_blockchain_interface(
    "ethereum",
    network="sepolia",
    provider_url="https://sepolia.infura.io/v3/YOUR_KEY",
    private_key="YOUR_PRIVATE_KEY",
    contract_address="DEPLOYED_CONTRACT_ADDRESS"
)

tx_id = blockchain.record_hash(
    "test_hash_123",
    datetime.now(),
    "camera_001"
)
print(f"Transaction: {tx_id}")
```

### ⏳ Phase A: Loopring Implementation (PLANNED)

The production zkRollup implementation for scalability.

#### Why Loopring?

- **Cost efficient**: ~$0.0001 per transaction vs $1-10 on Ethereum L1
- **High throughput**: 1000+ TPS vs 15 TPS on Ethereum L1
- **Fast finality**: <2 seconds vs 12+ seconds on Ethereum L1
- **Ethereum security**: Inherits Ethereum L1 security guarantees
- **Proven technology**: Production-ready, handling millions of transactions

#### Implementation Approach

**Option 1: Loopring DEX Smart Wallet API**

Use Loopring's existing smart wallet infrastructure:

```python
import requests
from loopring_sdk import LoopringClient

class LoopringBlockchain(BlockchainInterface):
    def __init__(self, network="mainnet", api_key=None):
        self.client = LoopringClient(network)
        self.api_key = api_key
        # Authenticate with API key
        
    def record_hash(self, image_hash, timestamp, camera_id, geolocation=None):
        # Use transfer with memo field to store hash
        # Or use NFT minting with metadata
        # This leverages existing Loopring infrastructure
```

**Option 2: Custom zkRollup Integration**

Deploy a custom contract on Loopring:

```python
# This would require:
# 1. Deploy custom contract to Loopring
# 2. Use Loopring's zkRollup SDK
# 3. Batch transactions for efficiency
```

**Option 3: Hybrid Approach**

- Use Ethereum L1 as fallback/anchor
- Use Loopring L2 for high-volume batching
- Periodically anchor L2 state to L1

#### Next Steps for Loopring

1. Research Loopring's current API capabilities
2. Contact Loopring team about custom use case
3. Evaluate cost/benefit of Loopring vs other zkRollups (zkSync, Starknet)
4. Prototype integration
5. Load testing at scale

## Integration with Other Modules

The blockchain module integrates with:

### Hash Module (`hash.py`)

```python
from hash import compute_image_hash
from blockchain import record_to_blockchain

# Compute hash
image_hash, timestamp = compute_image_hash(image_data)

# Record to blockchain
tx_id = record_to_blockchain(
    image_hash=image_hash,
    timestamp=timestamp,
    camera_id="camera_001",
    backend="mock"
)
```

### Camera Module (`camera.py`)

```python
from camera import CameraInterface

camera = CameraInterface(
    camera_id="camera_001",
    blockchain_backend="mock"
)

# Capture authenticates automatically
result = camera.capture_authenticated(
    output_path=Path("photo.jpg"),
    geolocation=(45.5, -122.6)
)

print(f"Transaction: {result.transaction_id}")
```

## Performance Considerations

### Mock Backend
- **Latency**: ~0ms (in-memory)
- **Throughput**: Limited by Python performance
- **Cost**: Free
- **Use for**: Testing, development, demos

### Ethereum Backend
- **Latency**: 12-15 seconds (block time)
- **Throughput**: ~15 TPS
- **Cost**: $1-10 per transaction (depending on gas)
- **Use for**: Testnet validation, initial pilot

### Loopring Backend (Target)
- **Latency**: 1-2 seconds
- **Throughput**: 1000+ TPS
- **Cost**: ~$0.0001 per transaction
- **Use for**: Production deployment

## Security Considerations

### Private Key Management

```python
# ❌ BAD: Never hardcode private keys
blockchain = EthereumBlockchain(
    private_key="0x1234..."  # DON'T DO THIS
)

# ✅ GOOD: Use environment variables
import os
blockchain = EthereumBlockchain(
    private_key=os.environ.get("ETH_PRIVATE_KEY")
)

# ✅ BETTER: Use key management service
from key_manager import get_signing_key
blockchain = EthereumBlockchain(
    private_key=get_signing_key()
)
```

### Rate Limiting

```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=100, period=60)  # 100 calls per minute
def record_with_rate_limit(blockchain, *args):
    return blockchain.record_hash(*args)
```

### Input Validation

```python
def validate_image_hash(hash_str: str) -> bool:
    """Validate hash format before recording."""
    if len(hash_str) != 64:  # SHA-256 is 64 hex chars
        return False
    try:
        int(hash_str, 16)  # Must be valid hex
        return True
    except ValueError:
        return False
```

## Error Handling

```python
from blockchain import (
    get_blockchain_interface,
    TransactionFailedError,
    VerificationError
)

try:
    tx_id = blockchain.record_hash(...)
except TransactionFailedError as e:
    # Handle transaction failure
    logger.error(f"Transaction failed: {e}")
    # Retry logic here
except ConnectionError as e:
    # Handle network issues
    logger.error(f"Network error: {e}")
    # Queue for later retry
```

## Monitoring and Analytics

```python
class MonitoredBlockchain:
    """Wrapper to add monitoring to any blockchain backend."""
    
    def __init__(self, blockchain: BlockchainInterface):
        self.blockchain = blockchain
        self.metrics = {
            "total_records": 0,
            "total_verifications": 0,
            "failed_records": 0,
            "failed_verifications": 0
        }
    
    def record_hash(self, *args, **kwargs):
        try:
            result = self.blockchain.record_hash(*args, **kwargs)
            self.metrics["total_records"] += 1
            return result
        except Exception as e:
            self.metrics["failed_records"] += 1
            raise
```

## Next Steps

### Immediate (This Week)
1. ✅ Review and test mock implementation
2. ⬜ Set up Ethereum development environment
3. ⬜ Deploy smart contract to Sepolia testnet
4. ⬜ Complete Ethereum backend implementation

### Short Term (This Month)
1. ⬜ Integration testing with hash and camera modules
2. ⬜ Performance benchmarking on testnet
3. ⬜ Document gas optimization strategies
4. ⬜ Create deployment guide

### Medium Term (Next Quarter)
1. ⬜ Research Loopring integration options
2. ⬜ Prototype zkRollup implementation
3. ⬜ Load testing at scale (1000+ TPS)
4. ⬜ Cost analysis for production deployment

### Long Term
1. ⬜ Production Loopring deployment
2. ⬜ Multi-chain support (Polygon, Arbitrum, etc.)
3. ⬜ Decentralized infrastructure (IPFS for metadata)
4. ⬜ DAO governance for protocol upgrades

## Contributing

We need help with:

- **Smart contract development** - Solidity experience
- **zkRollup integration** - Loopring, zkSync, or Starknet experience
- **Testing** - Load testing, security audits
- **Gas optimization** - Reducing transaction costs
- **Documentation** - Implementation guides, tutorials

See open issues tagged `blockchain` on GitHub.

## Resources

### Documentation
- [Ethereum web3.py docs](https://web3py.readthedocs.io/)
- [Loopring documentation](https://docs.loopring.io/)
- [Hardhat documentation](https://hardhat.org/docs)

### Testnets
- [Sepolia faucet](https://sepoliafaucet.com/)
- [Sepolia explorer](https://sepolia.etherscan.io/)

### Tools
- [Remix IDE](https://remix.ethereum.org/) - Solidity development
- [Hardhat](https://hardhat.org/) - Smart contract deployment
- [Infura](https://infura.io/) - Ethereum node access
- [Alchemy](https://www.alchemy.com/) - Alternative node provider

## Questions?

Contact: samryan.pdx@proton.me
