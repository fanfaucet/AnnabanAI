# AetherOS MVP — Sovereign Cryptographic Communication Stack

AetherOS MVP is an end-to-end cryptographic client/server stack with verifiable provenance, replay defense, and signature-based identity checks.

## Repository Layout

```text
aetheros-mvp/
  backend/
  android/
  scripts/
  network/ (optional phase 2)
```

## Backend Setup (Node.js)

1. Install Node.js 20+.
2. Configure environment:
   ```bash
   cd backend
   cp .env.example .env
   npm install
   ```
3. Run startup gate + server:
   ```bash
   ../scripts/start.sh
   ```

Server endpoints:
- `GET /pubkey`: returns server Curve25519 and Ed25519 public keys.
- `POST /message`: accepts encrypted client envelope and returns encrypted signed response.

## Android Setup (Kotlin)

1. Open `android/` in Android Studio (Giraffe+ recommended).
2. Sync Gradle and install dependencies.
3. Ensure emulator/device can hit backend.
   - Android emulator default host loopback: `10.0.2.2`.
4. Run app and send intents (`time`, `status`).

## How to find local IP (physical device)

- macOS/Linux:
  ```bash
  ip addr | rg "inet "
  ```
- Windows (PowerShell):
  ```powershell
  ipconfig
  ```

Update `baseUrl` in `MainActivity.kt` for device testing.

## Security Model

### 1) Encryption (nacl.box)

- Client encrypts request with server Curve25519 public key.
- Server decrypts with its Curve25519 secret key.
- Server encrypts response back to client key.
- Primitive: Curve25519 + XSalsa20-Poly1305.

### 2) Signatures (Ed25519)

- Client signs plaintext message before encrypting envelope.
- Server verifies signature after decryption.
- Server signs response plaintext.
- Android verifies and renders:
  - `🛡️ Verified` if valid.
  - `⚠️ Unverified` if invalid.

### 3) Tamper-Proof Ledger

- `heritage_ledger.log` is append-only JSON-lines.
- Each entry stores `timestamp`, `msgId`, `prevHash`, `hash`.
- `hash = SHA256(JSON(entry + prevHash))`.
- Modifying historical records breaks downstream hashes.

### 4) Startup Audit Gate

- Server runs full chain verification before starting.
- If invalid, startup aborts with exit code `1`.

### 5) Replay Protection

- Checks duplicate `msgId` and timestamp drift (`±30s` default).
- Violations are rejected with `400`/error payload.

## Scripts

- `scripts/start.sh` — verifies ledger then starts backend.
- `scripts/verify_ledger.sh` — runs manual audit.
- `scripts/reset_ledger.sh` — empties ledger file (dev-only).

## Testing Checklist

- [ ] Start backend with `scripts/start.sh`.
- [ ] `GET /pubkey` returns both public keys.
- [ ] Send `status` from Android and receive valid response.
- [ ] Badge shows `🛡️ Verified` on normal flow.
- [ ] Re-send same envelope -> replay rejection.
- [ ] Edit a ledger line manually, then restart server -> startup refusal.

## Optional Phase 2: Multi-Node Network

`network/` includes a minimal trust + relay design:

- Signed node registration with public key identity.
- Verified peer list exchange.
- Signature-checked relay envelopes.

This enables sovereign nodes to federate without a centralized trust anchor.
