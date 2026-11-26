# AnnabanOS External Agent Gateway

Status: prototype / local simulation. External effects are disabled.

## Security contract

- Agent login verifies an API-key digest and a short-lived HMAC-SHA256 signed token.
- Every valid login creates a **pending** session. Login never approves privileges.
- A human must explicitly approve a non-empty subset of the requested, allow-listed capabilities.
- Capabilities such as kernel boot, policy editing, audit editing, scheduler access, agent spawning, external execution, and credential reading are denied.
- Session state is in memory; restarting the process invalidates sessions.
- Task submission only records an advisory task hash and metadata. It does not call Codex, Grok, Claude, run code, or dispatch tasks.
- The JSONL audit ledger chains record hashes. This is tamper-evident, not tamper-proof. Existing ledgers are rejected rather than silently appended without chain verification.

## Local test

From the repository root:

```bash
python -m unittest annabanos.tests.test_external_agent_gateway -v
```

## Integration boundary

Provider-specific identity verification and actual external-agent transport are intentionally not implemented. HMAC uses a shared secret and is suitable only for this prototype; production federation should use provider-supported asymmetric signatures, managed key rotation, durable nonce storage, authenticated human approval, OS-level sandboxing, and independent audit checkpoints.

The policy JSON is a reference allow-list. Load and validate it explicitly when wiring configuration; this prototype does not silently trust configuration as an authority grant.
