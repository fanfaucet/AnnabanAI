# AnnabanAI Human Sovereignty Layer (HSL)

This directory contains a reusable HSL execution gate and integration tests.

## State and enforcement contract

- A model recommendation is not authorization.
- Required evidence must be attached before authorization can be requested.
- Authorization is an Ed25519 signature over a canonical payload bound to the exact action, target, recommendation hash, evidence hash, expiry, and unique nonce.
- Execution is denied unless the gate is in `AUTHORIZED` with a valid, unexpired authorization.
- Human rejection blocks execution.
- The gate emits a hash-linked event sequence and provides an independent in-process verifier.

## Current payment integration

The Stripe webhook path creates an HSL workflow record for each accepted payment event. A verified, confirmed payment with required evidence reaches `AUTHORIZATION_PENDING` and remains `awaiting_human_approval`. The webhook does not fulfill orders or trigger external side effects.

The payment integration does **not** yet expose a human approval endpoint or connect an approval key to order fulfillment. That is intentional: the gate must be connected to the real fulfillment boundary before fulfillment can be enabled.

## Run integration tests

From `aetheros-mvp/backend`:

```sh
npm install
npm run test:integration
```

This runs the HSL workflow integration tests and the existing local HTTP payment-service simulation. The payment simulation uses synthetic events and does not contact Stripe or process real payments.

## Scope and limitations

This is an implementation increment, not a production security certification. The payment audit log remains a local JSONL hash chain; the HSL event head is recorded with the payment record, but no external immutable anchor is configured. The caller must enforce the gate immediately before any real side effect. Do not treat an in-process hash chain as protection against a privileged actor who can rewrite the complete ledger.
