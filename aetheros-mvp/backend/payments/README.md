# AnnabanAI Payment Links (setup required)

This module adds payment-link discovery, pilot/user lead intake, and a hash-chained audit record for verified Stripe webhook events. It does not create Stripe products, set prices, take card details, or automatically provision paid access.

## Offers

Configure both links in the Stripe Dashboard, then set:

- `STRIPE_PILOT_PAYMENT_LINK`: hosted link for the business pilot.
- `STRIPE_USER_PAYMENT_LINK`: hosted link for the individual-user plan (one-time or recurring, as configured in Stripe).

Only HTTPS URLs beginning with `https://buy.stripe.com/` are returned to clients. No price is assumed in this repository. Confirm pilot scope, written terms, and price with the customer before sharing a pilot link.

## Environment

Copy `.env.example` to `.env` in this directory and configure values privately:

- `PAYMENTS_PORT` (default 3100)
- `PAYMENTS_AUDIT_PATH` (default `./payments-ledger.jsonl`)
- `PAYMENTS_LEADS_PATH` (default `./pilot-leads.jsonl`)
- `STRIPE_WEBHOOK_SECRET` (signing secret from Stripe Dashboard)
- `STRIPE_PILOT_PAYMENT_LINK`
- `STRIPE_USER_PAYMENT_LINK`
- `PAYMENTS_ADMIN_TOKEN` (long random token for the read-only audit endpoint)

Never commit `.env` or expose `PAYMENTS_ADMIN_TOKEN`.

## Start

From `aetheros-mvp/backend`:

```bash
npm install
npm run payments
```

The service listens on port 3100 by default.

## Local simulation

Run from `aetheros-mvp/backend` after installing dependencies:

```bash
npm run simulate:payments
```

This starts the local service with synthetic credentials and temporary files, then checks offer setup state, consent enforcement, valid/invalid webhook signatures, duplicate event handling, audit recording, and the human-approval hold. It does not contact Stripe or move money. The simulation harness is committed but has not been executed in this environment; treat its results as unverified until run locally.

## Routes

- `GET /health` — configuration status only.
- `GET /offers` — public offer descriptions and configured payment links.
- `POST /leads` — lead capture. Requires name, email, offer (`pilot` or `user`), and `consent_to_contact: true`.
- `POST /webhooks/stripe` — Stripe webhook endpoint; verifies the raw-body HMAC signature and timestamp, deduplicates event IDs, and records relevant events.
- `GET /admin/audit` — read-only ledger export, protected by `Authorization: Bearer <PAYMENTS_ADMIN_TOKEN>`.

## Stripe setup and human approval

In Stripe Dashboard, create the Payment Links manually, then configure a webhook endpoint at `https://YOUR-HOST/webhooks/stripe`. Subscribe to:
- `checkout.session.completed`
- `checkout.session.async_payment_succeeded`
- `checkout.session.async_payment_failed`
- `invoice.paid`
- `invoice.payment_failed`
- `customer.subscription.deleted`

Use the webhook signing secret as `STRIPE_WEBHOOK_SECRET`. Verify in Stripe test mode first.

Webhook records are evidence of received Stripe events, not a substitute for reconciling the merchant dashboard. A successful payment is recorded as `awaiting_human_approval`; this service intentionally does not grant access, start work, issue refunds, or sign contracts automatically. Human review must confirm the customer, offer, terms, and any refund or dispute status before fulfillment.

## Audit design and limits

Lead and payment records are append-only JSONL entries with a SHA-256 previous-entry chain. This is tamper-evident, not tamper-proof: protect the host and files, back them up, and periodically verify/export them independently. The admin route currently returns the stored records; it does not claim an independent reconciliation of Stripe balances or payouts.

This is a starter integration. Before production use, add deployment-specific rate limiting, retention/access controls for personal data, operational monitoring, and automated tests. Do not collect card numbers or security codes in AnnabanAI.
