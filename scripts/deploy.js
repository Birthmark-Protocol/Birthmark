// scripts/deploy.js
/**
 * Hardhat deployment script for BirthmarkRegistry contract
 * 
 * Usage:
 *   npx hardhat run scripts/deploy.js --network sepolia
 */

const hre = require("hardhat");

async function main() {
  console.log("Deploying BirthmarkRegistry to", hre.network.name);
  
  // Get deployer account
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());
  
  // Deploy contract
  const BirthmarkRegistry = await hre.ethers.getContractFactory("BirthmarkRegistry");
  const registry = await BirthmarkRegistry.deploy();
  
  await registry.deployed();
  
  console.log("\n✅ BirthmarkRegistry deployed!");
  console.log("Contract address:", registry.address);
  console.log("Transaction hash:", registry.deployTransaction.hash);
  console.log("Block number:", registry.deployTransaction.blockNumber);
  
  // Wait for a few confirmations
  console.log("\nWaiting for confirmations...");
  await registry.deployTransaction.wait(5);
  console.log("✅ Confirmed!");
  
  // Verify contract on Etherscan (if not local network)
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("\n📝 Verifying contract on Etherscan...");
    console.log("Run this command to verify:");
    console.log(`npx hardhat verify --network ${hre.network.name} ${registry.address}`);
  }
  
  // Save deployment info
  const fs = require("fs");
  const deploymentInfo = {
    network: hre.network.name,
    contractAddress: registry.address,
    transactionHash: registry.deployTransaction.hash,
    blockNumber: registry.deployTransaction.blockNumber,
    deployer: deployer.address,
    timestamp: new Date().toISOString()
  };
  
  fs.writeFileSync(
    "deployment-info.json",
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log("\n💾 Deployment info saved to deployment-info.json");
  
  // Test the contract
  console.log("\n🧪 Testing contract...");
  
  const testHash = hre.ethers.utils.id("test_image_data");
  const timestamp = Math.floor(Date.now() / 1000);
  const cameraId = hre.ethers.utils.formatBytes32String("test_camera");
  
  console.log("Recording test hash...");
  const tx = await registry.recordHash(
    testHash,
    timestamp,
    cameraId,
    45523100,  // 45.5231 * 1e6
    -122676500, // -122.6765 * 1e6
    true
  );
  
  await tx.wait();
  console.log("✅ Test hash recorded");
  
  // Verify it
  const [found, ts, camId, lat, lon, hasGeo, blockNum] = await registry.verifyHash(testHash);
  
  if (found) {
    console.log("✅ Test hash verified!");
    console.log("  Timestamp:", ts.toString());
    console.log("  Camera ID:", hre.ethers.utils.parseBytes32String(camId));
    console.log("  Latitude:", lat.toNumber() / 1e6);
    console.log("  Longitude:", lon.toNumber() / 1e6);
    console.log("  Block:", blockNum.toString());
  }
  
  // Get stats
  const [total, blockNumber] = await registry.getStats();
  console.log("\n📊 Contract stats:");
  console.log("  Total records:", total.toString());
  console.log("  Current block:", blockNumber.toString());
  
  console.log("\n🎉 Deployment complete!");
  console.log("\nNext steps:");
  console.log("1. Save the contract address:", registry.address);
  console.log("2. Update blockchain.py with contract address and ABI");
  console.log("3. Test integration with Python code");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
