// hardhat.config.js
/**
 * Hardhat configuration for BirthmarkRegistry deployment
 * 
 * Setup:
 *   1. npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
 *   2. Create .env file with:
 *      SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_KEY
 *      PRIVATE_KEY=your_private_key
 *      ETHERSCAN_API_KEY=your_etherscan_key
 *   3. npx hardhat compile
 *   4. npx hardhat run scripts/deploy.js --network sepolia
 */

require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200  // Optimize for deployment cost vs execution cost
      }
    }
  },
  
  networks: {
    // Local Hardhat network for testing
    hardhat: {
      chainId: 31337
    },
    
    // Sepolia testnet
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL || "",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 11155111
    },
    
    // Goerli testnet (being deprecated)
    goerli: {
      url: process.env.GOERLI_RPC_URL || "",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 5
    },
    
    // Ethereum mainnet (for future production)
    mainnet: {
      url: process.env.MAINNET_RPC_URL || "",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 1
    }
  },
  
  // Etherscan verification
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY || ""
  },
  
  // Gas reporter (optional, for optimization)
  gasReporter: {
    enabled: process.env.REPORT_GAS === "true",
    currency: "USD",
    coinmarketcap: process.env.COINMARKETCAP_API_KEY || ""
  }
};
