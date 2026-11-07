const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '.env') });
const express = require('express');
const crypto = require('crypto');
const fs = require('fs');
const { HslExecutionGate } = require('../hsl/gate');

const app = express();
const port = Number(process.env.PAYMENTS_PORT || 3100);
const auditPath = path.resolve(process.env.PAYMENTS_AUDIT_PATH || './payments-ledger.jsonl');
const leadPath = path.resolve(process.env.PAYMENTS_LEADS_PATH || './pilot-leads.jsonl');
const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET || '';
const maxWebhookAgeSeconds = Number(process.env.STRIPE_WEBHOOK_TOLERANCE_SECONDS || 300);

const OFFERS = {
  pilot: {
    label: 'AnnabanAI Business Pilot',
    description: 'A scoped business pilot. Confirm scope, price, timeline, and terms with the customer before sharing the payment link.',
    url: process.env.STRIPE_PILOT_PAYMENT_LINK || ''
  },
  user: {
    label: 'AnnabanAI User Plan',
    description: 'An individual-user offer. Configure one-time or recurring terms in Stripe before sharing the payment link.',
    url: process.env.STRIPE_USER_PAYMENT_LINK || ''
  }
};

function readJsonl(filePath) {
  if (!fs.existsSync(filePath)) return [];
  const raw = fs.readFileSync(filePath, 'utf8').trim();
  if (!raw) return [];
  return raw.split('\n').filter(Boolean).map((line) => JSON.parse(line));
}

function appendHashChained(filePath, record) {
  const entries = readJsonl(filePath);
  const prevHash = entries.length ? entries[entries.length - 1].hash : null;
  const body = { ...record, prevHash };
  const hash = crypto.createHash('sha256').update(JSON.stringify(body)).digest('hex');
  const committed = { ...body, hash };
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.appendFileSync(filePath, JSON.stringify(committed) + '\n', { mode: 0o600 });
  return committed;
}

function verifyStripeSignature(rawBody, header, secret) {
  if (!secret || !header) return false;
  const parts = Object.fromEntries(header.split(',').map((item) => {
    const index = item.indexOf('=');
    return index === -1 ? [item, ''] : [item.slice(0, index), item.slice(index + 1)];
  }));
  const timestamp = Number(parts.t);
  const signatures = header.split(',').filter((part) => part.startsWith('v1=')).map((part) => part.slice(3));
  if (!Number.isFinite(timestamp) || Math.abs(Date.now() / 1000 - timestamp) > maxWebhookAgeSeconds || !signatures.length) return false;
  const signedPayload = Buffer.concat([Buffer.from(String(timestamp) + '.'), rawBody]);
  const expected = crypto.createHmac('sha256', secret).update(signedPayload).digest();
  return signatures.some((signature) => {
    if (!/^[a-f0-9]{64}$/i.test(signature)) return false;
    const actual = Buffer.from(signature, 'hex');
    return actual.length === expected.length && crypto.timingSafeEqual(actual, expected);
  });
}

function auditEventIds() {
  return new Set(readJsonl(auditPath).map((entry) => entry.event_id).filter(Boolean));
}

// Keep this raw-body route before any JSON body parser so Stripe signatures can be verified.
app.post('/webhooks/stripe', express.raw({ type: 'application/json', limit: '1mb' }), (req, res) => {
  if (!webhookSecret) return res.status(503).json({ error: 'Stripe webhook is not configured' });
  if (!Buffer.isBuffer(req.body) || !verifyStripeSignature(req.body, req.get('stripe-signature'), webhookSecret)) {
    return res.status(400).json({ error: 'Invalid Stripe webhook signature' });
  }

  let event;
  try {
    event = JSON.parse(req.body.toString('utf8'));
  } catch {
    return res.status(400).json({ error: 'Invalid webhook JSON' });
  }
  if (!event.id || !event.type) return res.status(400).json({ error: 'Missing Stripe event identity' });
  if (auditEventIds().has(event.id)) return res.status(200).json({ received: true, duplicate: true });

  const object = event.data && event.data.object ? event.data.object : {};
  const allowedTypes = new Set([
    'checkout.session.completed',
    'checkout.session.async_payment_succeeded',
    'checkout.session.async_payment_failed',
    'invoice.paid',
    'invoice.payment_failed',
    'customer.subscription.deleted'
  ]);
  if (!allowedTypes.has(event.type)) {
    appendHashChained(auditPath, {
      timestamp: new Date().toISOString(),
      record_type: 'stripe_event_ignored',
      event_id: event.id,
      event_type: event.type,
      evidence_class: 'stripe_signature_verified',
      validation_status: 'verified_event_type_not_used',
      provenance: 'stripe_webhook'
    });
    return res.status(200).json({ received: true, recorded: true, ignored: true });
  }

  const paymentConfirmed =
    event.type === 'checkout.session.async_payment_succeeded' ||
    (event.type === 'checkout.session.completed' && object.payment_status === 'paid') ||
    event.type === 'invoice.paid';

  // Integrate the HSL gate into the real payment-event path. This creates a
  // recommendation/evidence/authorization-pending record only; it never fulfills
  // an order. A separate human-authorized fulfillment integration is required.
  const hsl = new HslExecutionGate({
    requiredEvidence: ['stripeEventId', 'stripeObjectId', 'signatureVerified', 'paymentConfirmed']
  });
  hsl.recommend({
    action: 'fulfill_paid_order',
    target: object.id || event.id,
    payload: { stripeEventId: event.id, eventType: event.type }
  });
  if (paymentConfirmed) {
    hsl.attachEvidence({
      stripeEventId: event.id,
      stripeObjectId: object.id || event.id,
      signatureVerified: true,
      paymentConfirmed: true
    });
  }
  const hslAudit = hsl.verifyEventChain();

  appendHashChained(auditPath, {
    timestamp: new Date().toISOString(),
    record_type: 'payment_event',
    event_id: event.id,
    event_type: event.type,
    stripe_object_id: object.id || null,
    payment_link: object.payment_link || null,
    customer_reference: object.client_reference_id || null,
    currency: object.currency || null,
    amount_total: Number.isInteger(object.amount_total) ? object.amount_total : null,
    payment_status: object.payment_status || object.status || null,
    payment_confirmed: paymentConfirmed,
    human_review_required: paymentConfirmed,
    fulfillment_status: paymentConfirmed ? 'awaiting_human_approval' : 'not_fulfilled',
    hsl_state: hsl.state,
    hsl_audit_head: hslAudit.headHash,
    hsl_audit_valid: hslAudit.valid,
    evidence_class: 'stripe_signature_verified',
    validation_status: 'verified_webhook_recorded',
    provenance: 'stripe_webhook'
  });
  return res.status(200).json({
    received: true,
    recorded: true,
    human_review_required: paymentConfirmed,
    hsl_state: hsl.state,
    fulfillment_status: paymentConfirmed ? 'awaiting_human_approval' : 'not_fulfilled'
  });
});

app.use(express.json({ limit: '32kb' }));

app.get('/health', (_req, res) => res.json({
  service: 'annabanai-payments',
  mode: 'payment-links-only',
  webhook_configured: Boolean(webhookSecret),
  status: 'setup_required_until_credentials_and_links_are_configured'
}));

app.get('/offers', (_req, res) => {
  res.json({
    offers: Object.entries(OFFERS).map(([key, offer]) => {
      const configuredUrl = /^https:\/\/buy\.stripe\.com\//.test(offer.url);
      return {
        key,
        label: offer.label,
        description: offer.description,
        payment_link_configured: configuredUrl,
        payment_url: configuredUrl ? offer.url : null,
        setup_required: !configuredUrl
      };
    })
  });
});

app.post('/leads', (req, res) => {
  const { name, email, organization, offer, use_case, consent_to_contact } = req.body || {};
  if (typeof name !== 'string' || name.trim().length < 1 || name.length > 120) return res.status(400).json({ error: 'A valid name is required' });
  if (typeof email !== 'string' || email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return res.status(400).json({ error: 'A valid email is required' });
  if (!['pilot', 'user'].includes(offer)) return res.status(400).json({ error: 'Offer must be pilot or user' });
  if (consent_to_contact !== true) return res.status(400).json({ error: 'Explicit consent to contact is required' });
  const leadId = crypto.randomUUID();
  appendHashChained(leadPath, {
    timestamp: new Date().toISOString(),
    record_type: 'lead_inquiry',
    lead_id: leadId,
    name: name.trim(),
    email: email.trim().toLowerCase(),
    organization: typeof organization === 'string' ? organization.trim().slice(0, 160) : '',
    offer,
    use_case: typeof use_case === 'string' ? use_case.trim().slice(0, 2000) : '',
    consent_to_contact: true,
    status: 'new',
    human_review_required: true,
    provenance: 'public_lead_form'
  });
  return res.status(201).json({ lead_id: leadId, status: 'received', next_step: 'A human must review the inquiry and confirm scope, pricing, and terms.' });
});

app.get('/admin/audit', (req, res) => {
  const expected = process.env.PAYMENTS_ADMIN_TOKEN || '';
  if (!expected || req.get('authorization') !== 'Bearer ' + expected) return res.status(401).json({ error: 'Unauthorized' });
  return res.json({ payments: readJsonl(auditPath), leads: readJsonl(leadPath) });
});

app.listen(port, () => console.log('AnnabanAI payment-link service listening on port ' + port));
