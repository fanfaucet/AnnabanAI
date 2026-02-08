"""Blockchain wallet capabilities for AnnabanAI.

This module provides an in-memory wallet abstraction that can be used to map
AnnabanAI agents to blockchain-style addresses and transactions without
requiring a live chain connection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import math
import secrets
from typing import Dict, List, Optional


@dataclass
class WalletTransaction:
    """Represents a transfer between two wallets."""

    tx_id: str
    sender_address: str
    recipient_address: str
    amount: float
    asset: str
    memo: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class AgentWallet:
    """Represents an AnnabanAI agent wallet profile."""

    agent_id: str
    address: str
    network: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class BlockchainWalletService:
    """Simple wallet manager for AnnabanAI simulations.

    The service keeps wallet data and transfers in memory and is intended for
    prototyping wallet-aware agent workflows.
    """

    def __init__(self, network: str = "annaban-testnet", default_asset: str = "ANNA") -> None:
        self.network = network
        self.default_asset = default_asset
        self.wallets: Dict[str, AgentWallet] = {}
        self.balances: Dict[str, float] = {}
        self.ledger: List[WalletTransaction] = []

    def create_wallet(self, agent_id: str, starting_balance: float = 0.0) -> AgentWallet:
        """Create a deterministic wallet address for an agent."""
        if agent_id in self.wallets:
            return self.wallets[agent_id]

        address_seed = f"{agent_id}:{secrets.token_hex(16)}:{self.network}".encode("utf-8")
        address = "0x" + hashlib.sha256(address_seed).hexdigest()[:40]

        wallet = AgentWallet(agent_id=agent_id, address=address, network=self.network)
        self.wallets[agent_id] = wallet
        self.balances[address] = float(starting_balance)
        return wallet

    def get_wallet(self, agent_id: str) -> Optional[AgentWallet]:
        """Return wallet details for an agent if present."""
        return self.wallets.get(agent_id)

    def get_balance(self, address: str) -> float:
        """Return the balance of an address."""
        return self.balances.get(address, 0.0)

    def transfer(
        self,
        sender_address: str,
        recipient_address: str,
        amount: float,
        memo: str = "",
        asset: Optional[str] = None,
    ) -> WalletTransaction:
        """Transfer funds between wallets and record on the local ledger."""
        try:
            amount_value = float(amount)
        except (TypeError, ValueError) as exc:
            raise ValueError("Transfer amount must be a finite number") from exc

        if not math.isfinite(amount_value):
            raise ValueError("Transfer amount must be a finite number")
        if amount_value <= 0:
            raise ValueError("Transfer amount must be positive")

        if sender_address not in self.balances:
            raise ValueError("Unknown sender address")
        if recipient_address not in self.balances:
            raise ValueError("Unknown recipient address")
        if self.balances[sender_address] < amount_value:
            raise ValueError("Insufficient funds")

        self.balances[sender_address] -= amount_value
        self.balances[recipient_address] += amount_value

        payload = (
            f"{sender_address}:{recipient_address}:{amount_value}:{datetime.utcnow().isoformat()}:{memo}"
        )
        tx_id = "tx_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]

        tx = WalletTransaction(
            tx_id=tx_id,
            sender_address=sender_address,
            recipient_address=recipient_address,
            amount=amount_value,
            asset=asset or self.default_asset,
            memo=memo,
        )
        self.ledger.append(tx)
        return tx

    def list_transactions(self, address: Optional[str] = None) -> List[WalletTransaction]:
        """List all transactions, optionally filtered by address."""
        if address is None:
            return list(self.ledger)

        return [
            tx
            for tx in self.ledger
            if tx.sender_address == address or tx.recipient_address == address
        ]
