from blockchain_wallet import BlockchainWalletService


def test_transfer_and_balances():
    # Create the wallet service and two wallets
    wallets = BlockchainWalletService(network="annaban-testnet", default_asset="ANNA")

    alice = wallets.create_wallet("alice", starting_balance=100)
    bob = wallets.create_wallet("bob", starting_balance=10)

    # Perform a transfer and inspect the returned transaction
    tx = wallets.transfer(alice.address, bob.address, 7.5, memo="Coordination bonus")

    assert tx.tx_id.startswith("tx_")
    assert tx.amount == 7.5
    assert tx.asset == "ANNA"

    # Check balances updated correctly
    assert wallets.get_balance(alice.address) == 92.5
    assert wallets.get_balance(bob.address) == 17.5

    # Ensure the transaction appears in the ledger for the sender
    txs = wallets.list_transactions(alice.address)
    assert any(t.tx_id == tx.tx_id for t in txs)
