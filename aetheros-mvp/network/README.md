# AetherOS Phase 2 Network (Optional)

This folder provides a minimal multi-node trust network:

- `config.example.js`: node identity, endpoint, port, and static peers.
- `node.js`: Express node service with identity bootstrap, registration, peer list, and relay endpoint.
- `registry.js`: signed node identity verification and registration.
- `relay.js`: signature-verified relay forwarding.

## Run a Node

```bash
cd network
node node.js
```

For multiple nodes, copy `config.example.js` per instance and adjust `nodeId`, `port`, and `endpoint`.
