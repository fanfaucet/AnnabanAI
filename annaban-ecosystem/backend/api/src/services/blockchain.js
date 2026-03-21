const { ethers } = require('ethers');

const ABI = [
  'function mintDecision(address to, string memory decisionHash, uint256 confidenceBps, uint256 ethicalBps) public returns (uint256)'
];

async function mintDecisionNFT(payload) {
  const { MINT_RPC_URL, MINT_PRIVATE_KEY, MINT_CONTRACT } = process.env;
  if (!MINT_RPC_URL || !MINT_PRIVATE_KEY || !MINT_CONTRACT) {
    return { skipped: true, reason: 'missing blockchain env vars' };
  }

  const provider = new ethers.JsonRpcProvider(MINT_RPC_URL);
  const wallet = new ethers.Wallet(MINT_PRIVATE_KEY, provider);
  const contract = new ethers.Contract(MINT_CONTRACT, ABI, wallet);

  const tx = await contract.mintDecision(
    wallet.address,
    payload.decisionHash,
    Math.round((payload.confidence || 0) * 10000),
    Math.round((payload.ethicalScore || 0) * 10000)
  );
  const receipt = await tx.wait();
  return { txHash: receipt.hash, blockNumber: receipt.blockNumber };
}

module.exports = { mintDecisionNFT };
