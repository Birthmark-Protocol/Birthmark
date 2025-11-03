# Ethereum Backend Setup Guide

## Overview

This guide walks through setting up the Ethereum backend (Phase B) for the Birthmark Protocol blockchain module.

## Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- Sepolia testnet ETH (from faucet)
- Infura or Alchemy account (for RPC access)

## Quick Start

### 1. Install Dependencies

```bash
# Node.js dependencies for smart contract
npm init -y
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox dotenv

# Python dependencies for integration
pip install web3 python-dotenv
```

### 2. Initialize Hardhat Project

```bash
npx hardhat init
# Select: Create a JavaScript project
```

### 3. Copy Files

```bash
# Copy the smart contract
cp BirthmarkRegistry.sol contracts/

# Copy deployment script
cp deploy.js scripts/

# Copy configuration
cp hardhat.config.js .
```

### 4. Create .env File

```bash
# .env
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
PRIVATE_KEY=your_private_key_here
ETHERSCAN_API_KEY=your_etherscan_key
```

**⚠️ SECURITY WARNING**: Never commit .env files to Git!

```bash
echo ".env" >> .gitignore
```

### 5. Get Testnet ETH

Visit Sepolia faucets:
- https://sepoliafaucet.com/
- https://faucet.sepolia.dev/
- https://sepolia-faucet.pk910.de/

You'll need ~0.1 Sepolia ETH for deployment and testing.

### 6. Compile Contract

```bash
npx hardhat compile
```

Expected output:
```
Compiled 1 Solidity file successfully
```

### 7. Deploy to Sepolia

```bash
npx hardhat run scripts/deploy.js --network sepolia
```

Expected output:
```
Deploying BirthmarkRegistry to sepolia
Deploying with account: 0x...
Contract address: 0x...
✅ BirthmarkRegistry deployed!
```

**Save the contract address!** You'll need it for Python integration.

### 8. Verify on Etherscan

```bash
npx hardhat verify --network sepolia CONTRACT_ADDRESS
```

This makes your contract code visible on Etherscan.

## Python Integration

### Update blockchain.py

Once deployed, update the `EthereumBlockchain` class:

```python
# In blockchain.py, update EthereumBlockchain.__init__

# Load contract ABI
with open('artifacts/contracts/BirthmarkRegistry.sol/BirthmarkRegistry.json') as f:
    contract_json = json.load(f)
    abi = contract_json['abi']

# Create contract instance
self.contract = self.w3.eth.contract(
    address=contract_address,
    abi=abi
)

# Set up account
self.account = self.w3.eth.account.from_key(private_key)
```

### Test Integration

```python
from blockchain import get_blockchain_interface
from datetime import datetime

# Initialize Ethereum backend
blockchain = get_blockchain_interface(
    "ethereum",
    network="sepolia",
    provider_url="https://sepolia.infura.io/v3/YOUR_KEY",
    private_key="YOUR_PRIVATE_KEY",
    contract_address="DEPLOYED_CONTRACT_ADDRESS"
)

# Test recording
tx_id = blockchain.record_hash(
    image_hash="abc123...",
    timestamp=datetime.now(),
    camera_id="test_camera",
    geolocation=(45.5231, -122.6765)
)

print(f"Transaction: https://sepolia.etherscan.io/tx/{tx_id}")

# Test verification
record = blockchain.verify_hash("abc123...")
if record:
    print(f"Verified! Camera: {record.camera_id}")
```

## Smart Contract Details

### BirthmarkRegistry Functions

**recordHash()**
- Records a single image hash
- Gas cost: ~80,000-100,000 gas
- Cost at 20 gwei: ~$0.50-1.00 (varies with ETH price)

**batchRecordHashes()**
- Records multiple hashes in one transaction
- Gas cost: ~60,000 + 50,000 per hash
- More efficient for bulk operations

**verifyHash()**
- Read-only, no gas cost
- Returns full record if found

**batchVerifyExistence()**
- Check multiple hashes at once
- Read-only, no gas cost
- Returns boolean array

### Data Structure

```solidity
struct BirthmarkRecord {
    bytes32 imageHash;      // 32 bytes
    uint256 timestamp;      // 32 bytes
    bytes32 cameraId;       // 32 bytes
    int256 latitude;        // 32 bytes (scaled by 1e6)
    int256 longitude;       // 32 bytes (scaled by 1e6)
    bool hasGeolocation;    // 1 byte
    uint256 blockNumber;    // 32 bytes
}
```

Total: ~193 bytes per record on-chain

### Gas Optimization

The contract includes several optimizations:
- Packed data types
- Efficient mappings
- Batch operations
- Optional geolocation

## Cost Analysis

### Sepolia Testnet (Free)
- Gas: Free testnet gas
- Perfect for development

### Ethereum Mainnet
- Gas price: 20-100 gwei typically
- Single record: $0.50-5.00
- Batch (10): $2.00-10.00
- **Not recommended** for production due to cost

### Why We Need zkRollup (Phase A)
- Loopring: ~$0.0001 per transaction
- 1000x cheaper than Ethereum L1
- This is why Phase A (Loopring) is the target

## Testing

### Local Testing

```bash
# Start local Hardhat node
npx hardhat node

# In another terminal, deploy locally
npx hardhat run scripts/deploy.js --network localhost
```

### Write Tests

```javascript
// test/BirthmarkRegistry.test.js
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("BirthmarkRegistry", function () {
  it("Should record and verify a hash", async function () {
    const BirthmarkRegistry = await ethers.getContractFactory("BirthmarkRegistry");
    const registry = await BirthmarkRegistry.deploy();
    
    const hash = ethers.utils.id("test_image");
    const timestamp = Math.floor(Date.now() / 1000);
    const cameraId = ethers.utils.formatBytes32String("camera_001");
    
    await registry.recordHash(hash, timestamp, cameraId, 45523100, -122676500, true);
    
    const [found, ts] = await registry.verifyHash(hash);
    expect(found).to.equal(true);
    expect(ts).to.equal(timestamp);
  });
});
```

Run tests:
```bash
npx hardhat test
```

## Monitoring

### View on Etherscan

Your deployed contract: `https://sepolia.etherscan.io/address/CONTRACT_ADDRESS`

Monitor:
- Recent transactions
- Gas usage
- Total records
- Events emitted

### Event Indexing

The contract emits events for off-chain indexing:

```javascript
event HashRecorded(
    bytes32 indexed imageHash,
    uint256 timestamp,
    bytes32 indexed cameraId,
    bool hasGeolocation,
    uint256 blockNumber
);
```

Use The Graph or similar to index events for fast queries.

## Security Considerations

### Private Key Management

**Never:**
- Hardcode private keys
- Commit .env files
- Share keys in plain text

**Instead:**
- Use environment variables
- Use hardware wallets for production
- Consider multi-sig wallets

### Smart Contract Security

The contract includes:
- Duplicate prevention
- Input validation
- Event emission for transparency
- No upgrade mechanism (immutable by default)

Consider a professional audit before mainnet deployment.

## Troubleshooting

### "Insufficient funds"
- Get more Sepolia ETH from faucets
- Check account balance: `npx hardhat run scripts/check-balance.js`

### "Nonce too high"
- Reset your Hardhat network
- Clear transaction history

### "Contract not verified"
- Run verification again
- Check Etherscan API key
- Wait a few minutes after deployment

### "Connection timeout"
- Check RPC URL
- Verify Infura/Alchemy is working
- Try different RPC provider

## Next Steps

1. ✅ Deploy to Sepolia
2. ⬜ Complete Python integration
3. ⬜ Write integration tests
4. ⬜ Benchmark performance
5. ⬜ Document gas costs
6. ⬜ Plan migration to zkRollup

## Resources

- [Hardhat Documentation](https://hardhat.org/docs)
- [Ethers.js Documentation](https://docs.ethers.io/)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Sepolia Explorer](https://sepolia.etherscan.io/)
- [Solidity Documentation](https://docs.soliditylang.org/)

## Support

Questions about Ethereum backend setup?
- Review: docs/BLOCKCHAIN_IMPLEMENTATION.md
- GitHub Issues: Tag with `blockchain` and `ethereum`
- Email: samryan.pdx@proton.me
