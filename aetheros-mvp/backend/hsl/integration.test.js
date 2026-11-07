'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const { HslExecutionGate, STATES, canonicalJson } = require('./gate');

function setup({ now = 1_800_000_000_000 } = {}) {
  const keys = crypto.generateKeyPairSync('ed25519');
  let clockNow = now;
  const gate = new HslExecutionGate({
    publicKey: keys.publicKey,
    requiredEvidence: ['caseId', 'evidenceSource'],
    clock: () => clockNow
  });
  const start = () => {
    assert.equal(gate.recommend({
      action: 'release_payment',
      target: 'pilot-order-42',
      payload: { amountMinor: 1234, currency: 'USD' }
    }).allowed, true);
    assert.equal(gate.attachEvidence({
      caseId: 'case-42',
      evidenceSource: 'synthetic-integration-fixture',
      paymentStatus: 'paid'
    }).state, STATES.AUTHORIZATION_PENDING);
  };
  const sign = (payload) => crypto.sign(null, Buffer.from(canonicalJson(payload)), keys.privateKey).toString('base64');
  const approve = (overrides = {}) => {
    const payload = gate.createAuthorizationPayload({
      approver: 'integration-test-human',
      nonce: crypto.randomUUID(),
      expiresAt: clockNow + 60_000,
      ...overrides
    });
    return { payload, signature: sign(payload) };
  };
  return { gate, start, approve, sign, advance: (ms) => { clockNow += ms; } };
}

test('integration: side effect gate blocks execution before signed human approval', () => {
  const { gate, start } = setup();
  start();
  const result = gate.execute();
  assert.equal(result.allowed, false);
  assert.equal(gate.state, STATES.AUTHORIZATION_PENDING);
});

test('integration: valid scoped human signature permits the execution gate', () => {
  const { gate, start, approve } = setup();
  start();
  const { payload, signature } = approve();
  assert.equal(gate.authorize(payload, signature).allowed, true);
  assert.equal(gate.execute().allowed, true);
  assert.equal(gate.state, STATES.EXECUTING);
  assert.equal(gate.complete({ resultHash: 'synthetic-result-hash' }).state, STATES.COMPLETED);
});

test('integration: required evidence omission prevents authorization request', () => {
  const { gate } = setup();
  gate.recommend({ action: 'release_payment', target: 'pilot-order-42', payload: {} });
  const result = gate.attachEvidence({ caseId: 'case-42' });
  assert.equal(result.allowed, false);
  assert.equal(result.reason, 'required_evidence_missing');
  assert.equal(gate.state, STATES.RECOMMENDATION);
  assert.equal(gate.execute().allowed, false);
});

test('integration: approval bound to a different target is rejected', () => {
  const { gate, start, approve } = setup();
  start();
  const { payload, signature } = approve({ target: 'different-order' });
  const result = gate.authorize(payload, signature);
  assert.equal(result.allowed, false);
  assert.equal(result.reason, 'authorization_scope_mismatch');
  assert.equal(gate.execute().allowed, false);
});

test('integration: expired authorization cannot pass the execution gate', () => {
  const { gate, start, approve, advance } = setup();
  start();
  const { payload, signature } = approve();
  assert.equal(gate.authorize(payload, signature).allowed, true);
  advance(61_000);
  const result = gate.execute();
  assert.equal(result.allowed, false);
  assert.equal(result.reason, 'authorization_expired_before_execution');
  assert.equal(gate.state, STATES.REJECTED);
});

test('integration: human rejection blocks execution', () => {
  const { gate, start } = setup();
  start();
  assert.equal(gate.reject({ approver: 'integration-test-human', reason: 'scope_not_approved' }).state, STATES.REJECTED);
  assert.equal(gate.execute().allowed, false);
});

test('integration: audit events can be independently reconstructed', () => {
  const { gate, start, approve } = setup();
  start();
  const { payload, signature } = approve();
  gate.authorize(payload, signature);
  gate.execute();
  gate.complete();
  assert.equal(gate.verifyEventChain().valid, true);

  const exported = gate.exportAudit();
  const { sha256 } = require('./gate');
  let previousHash = 'GENESIS';
  for (const event of exported) {
    assert.equal(event.previousHash, previousHash);
    const { hash, ...body } = event;
    assert.equal(sha256(body), hash);
    previousHash = hash;
  }
  exported[1].detail.action = 'tampered';
  const alteredBody = { ...exported[1] };
  delete alteredBody.hash;
  assert.notEqual(sha256(alteredBody), exported[1].hash);
});

test('integration: event-chain verifier detects altered records', () => {
  const { gate, start } = setup();
  start();
  const events = gate.events;
  events[0].detail.state = 'AUTHORIZED';
  assert.equal(gate.verifyEventChain().valid, false);
});
