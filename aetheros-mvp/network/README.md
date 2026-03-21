# AetherOS Phase 2 Network (Optional)

This module adds a minimal multi-node trust network:

- Node registration with signed identities.
- Peer list synchronization.
- Signed relay envelopes for forwarding payloads.

## Components

- `registry.js`: in-memory node registry + signature checks.
- `relay.js`: verifies sender identity and relays encrypted envelopes.

The design keeps each node sovereign (independent keypairs) while enabling verified routing.
