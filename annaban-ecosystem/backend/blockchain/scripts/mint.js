import dotenv from 'dotenv';
import { ethers } from 'ethers';

dotenv.config();

const ABI = ['function mintDecision(address to, string decisionHash, uint256 confidenceBps, uint256 ethicalBps) public returns (uint256)'];

async function main() {
  const provider = new ethers.JsonRpcProvider(process.env.MINT_RPC_URL);
  const wallet = new ethers.Wallet(process.env.MINT_PRIVATE_KEY, provider);
  const contract = new ethers.Contract(process.env.MINT_CONTRACT, ABI, wallet);

  const decisionHash = process.env.DECISION_HASH || 'demo-hash';
  const tx = await contract.mintDecision(wallet.address, decisionHash, 9000, 9100);
  const receipt = await tx.wait();
  console.log('Minted decision NFT:', receipt.hash);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
