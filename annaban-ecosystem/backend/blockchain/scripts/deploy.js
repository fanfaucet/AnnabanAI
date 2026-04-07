import hre from 'hardhat';

async function main() {
  const C = await hre.ethers.getContractFactory('DecisionNFT');
  const c = await C.deploy();
  await c.waitForDeployment();
  console.log('DecisionNFT deployed:', await c.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
