# Blockchain Wallet Capabilities

AnnabanAI now includes a lightweight blockchain wallet service for agents.

## Overview

The `BlockchainWalletService` supports wallet creation, balances, and local-ledger transfers so simulations can model wallet-native behaviors.

Core capabilities:
- Create deterministic blockchain-style addresses per agent.
- Track balances per address.
- Record signed-style transfer records in a transaction ledger.
- Query per-address transaction history.

> This is an in-memory simulation service intended for prototyping and testing. It does not broadcast to public blockchains.

## API

### `BlockchainWalletService(network: str = "annaban-testnet", default_asset: str = "ANNA")`
Create a wallet service instance.

### `create_wallet(agent_id: str, starting_balance: float = 0.0) -> AgentWallet`
Create or return a wallet for an agent.

### `get_wallet(agent_id: str) -> Optional[AgentWallet]`
Fetch wallet metadata for an agent.

### `get_balance(address: str) -> float`
Read the current balance for a wallet address.

### `transfer(sender_address: str, recipient_address: str, amount: float, memo: str = "", asset: Optional[str] = None) -> WalletTransaction`
Transfer funds from one wallet to another and append an immutable-style ledger event.

### `list_transactions(address: Optional[str] = None) -> List[WalletTransaction]`
Return all transactions, or only those associated with an address.

## Example

```python
from blockchain_wallet import BlockchainWalletService

wallets = BlockchainWalletService(network="annaban-testnet", default_asset="ANNA")

alice = wallets.create_wallet("alice", starting_balance=100)
bob = wallets.create_wallet("bob", starting_balance=10)

tx = wallets.transfer(alice.address, bob.address, 7.5, memo="Coordination bonus")

print(tx.tx_id)
print(wallets.get_balance(alice.address))
print(wallets.get_balance(bob.address))
```
