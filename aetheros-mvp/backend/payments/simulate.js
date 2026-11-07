// Local-only Stripe connection simulation. Uses synthetic events; never contacts Stripe.
const crypto = require('crypto');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const root = __dirname;
const secret = 'whsec_simulation_only_not_a_real_secret';
const port = 32000 + Math.floor(Math.random() * 20000);
const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'annabanai-stripe-sim-'));
const auditPath = path.join(tempDir, 'payments.jsonl');
const leadsPath = path.join(tempDir, 'leads.jsonl');

function sign(rawBody, timestamp = Math.floor(Date.now() / 1000)) {
  const digest = crypto.createHmac('sha256', secret).update(String(timestamp) + '.' + rawBody).digest('hex');
  return { timestamp, header: 't=' + timestamp + ',v1=' + digest };
}
function assert(condition, message) {
  if (!condition) throw new Error('SIMULATION FAILED: ' + message);
  process.stdout.write('PASS ' + message + '\n');
}
async function waitForServer(child, url) {
  for (let i = 0; i < 60; i += 1) {
    if (child.exitCode !== null) throw new Error('Payment service exited early');
    try {
      const response = await fetch(url + '/health');
      if (response.ok) return;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 150));
  }
  throw new Error('Payment service did not become ready');
}
async function main() {
  const child = spawn(process.execPath, [path.join(root, 'server.js')], {
    cwd: tempDir,
    env: {
      ...process.env,
      PAYMENTS_PORT: String(port),
      PAYMENTS_AUDIT_PATH: auditPath,
      PAYMENTS_LEADS_PATH: leadsPath,
      STRIPE_WEBHOOK_SECRET: secret,
      PAYMENTS_ADMIN_TOKEN: 'simulation-admin-token'
    },
    stdio: ['ignore', 'pipe', 'pipe']
  });
  let stderr = '';
  child.stderr.on('data', (chunk) => { stderr += chunk.toString(); });
  const base = 'http://127.0.0.1:' + port;
  try {
    await waitForServer(child, base);

    const offers = await (await fetch(base + '/offers')).json();
    assert(offers.offers.length === 2 && offers.offers.every((offer) => offer.setup_required), 'both offers are present but no invented payment links are exposed');

    const deniedLead = await fetch(base + '/leads', {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ name: 'Simulation User', email: 'sim@example.invalid', offer: 'user', consent_to_contact: false })
    });
    assert(deniedLead.status === 400, 'lead capture requires explicit contact consent');

    const lead = await fetch(base + '/leads', {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ name: 'Simulation User', email: 'sim@example.invalid', organization: 'Example Org', offer: 'pilot', use_case: 'Synthetic test only', consent_to_contact: true })
    });
    const leadBody = await lead.json();
    assert(lead.status === 201 && Boolean(leadBody.lead_id), 'consented synthetic lead is recorded');

    const event = {
      id: 'evt_simulated_checkout_001',
      type: 'checkout.session.completed',
      data: { object: {
        id: 'cs_simulated_001',
        payment_link: null,
        client_reference_id: leadBody.lead_id,
        currency: 'usd',
        amount_total: 1234,
        payment_status: 'paid'
      } }
    };
    const raw = JSON.stringify(event);
    const sig = sign(raw);
    const sendEvent = (header) => fetch(base + '/webhooks/stripe', {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'stripe-signature': header },
      body: raw
    });
    const bad = await sendEvent('t=' + sig.timestamp + ',v1=' + '0'.repeat(64));
    assert(bad.status === 400, 'invalid webhook signature is rejected');

    const good = await sendEvent(sig.header);
    const goodBody = await good.json();
    assert(good.status === 200 && goodBody.recorded && goodBody.human_review_required, 'valid synthetic payment event is recorded for human review');

    const duplicate = await sendEvent(sig.header);
    const duplicateBody = await duplicate.json();
    assert(duplicate.status === 200 && duplicateBody.duplicate, 'duplicate webhook delivery is idempotent');

    const audit = await fetch(base + '/admin/audit', { headers: { authorization: 'Bearer simulation-admin-token' } });
    const records = await audit.json();
    assert(records.leads.length === 1 && records.payments.length === 1, 'audit contains one lead and one deduplicated payment event');
    assert(records.payments[0].fulfillment_status === 'awaiting_human_approval', 'payment does not auto-provision or execute paid work');
    assert(records.payments[0].hsl_state === 'AUTHORIZATION_PENDING', 'confirmed payment enters the integrated HSL human-authorization state');
    assert(records.payments[0].hsl_audit_valid === true && Boolean(records.payments[0].hsl_audit_head), 'HSL workflow audit chain validates and its head is recorded');

    process.stdout.write('\nSIMULATION PASSED. No external Stripe API was called and no real payment occurred.\n');
  } finally {
    child.kill('SIGTERM');
    await new Promise((resolve) => child.once('exit', resolve));
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
}
main().catch((error) => {
  process.stderr.write((error.stack || error.message) + '\n');
  process.exitCode = 1;
});
