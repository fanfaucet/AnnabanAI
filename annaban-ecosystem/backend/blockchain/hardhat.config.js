import '@nomicfoundation/hardhat-toolbox';
import dotenv from 'dotenv';
dotenv.config();

export default {
  solidity: '0.8.24',
  networks: {
    amoy: {
      url: process.env.MINT_RPC_URL || '',
      accounts: process.env.MINT_PRIVATE_KEY ? [process.env.MINT_PRIVATE_KEY] : []
    }
  }
};
