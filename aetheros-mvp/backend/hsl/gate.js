/**
 * AnnabanAI Human Sovereignty Layer (HSL) execution gate.
 * Advisory/design reference integrated into backend workflows.
 * No side effects are performed by this module; callers must invoke execute()
 * immediately before any protected side effect and honor its result.
 */
'use strict';

const crypto = require('node:crypto');

const STATES = Object.freeze({
  IDLE: 'IDLE',
  RECOMMENDATION: 'RECOMMENDATION',
  EVIDENCE_ATTACHED: 'EVIDENCE_ATTACHED',
  AUTHORIZATION_PENDING: 'AUTHORIZATION_PENDING',
  AUTHORIZED: 'AUTHORIZED',
  EXECUTING: 'EXECUTING',
  COMPLETED: 'COMPLETED',
  REJECTED: 'REJECTED',
  SECURITY_VIOLATION: 'SECURITY_VIOLATION'
});

function canonicalJson(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return '[' + value.map(canonicalJson).join(',') + ']';
  return '{' + Object.keys(value).sort().map((key) =>
    JSON.stringify(key) + ':' + canonicalJson(value[key])
  ).join(',') + '}';
}

function sha256(value) {
  return crypto.createHash('sha256').update(
    typeof value === 'string' ? value : canonicalJson(value)
  ).digest('hex');
}

class HslExecutionGate {
  constructor({ publicKey, requiredEvidence = [], clock = () => Date.now() } = {}) {
    this.publicKey = publicKey;
    this.requiredEvidence = requiredEvidence;
    this.clock = clock;
    this.state = STATES.IDLE;
    this.recommendation = null;
    this.evidence = null;
    this.authorization = null;
    this.consumedNonces = new Set();
    this.events = [];
    this._record('STATE_INITIALIZED', { state: this.state });
  }

  _record(type, detail = {}) {
    const previousHash = this.events.length ? this.events[this.events.length - 1].hash : 'GENESIS';
    const body = { sequence: this.events.length + 1, timestamp_ms: this.clock(), type, state: this.state, detail, previousHash };
    const hash = sha256(body);
    this.events.push({ ...body, hash });
  }

  _violation(reason) {
    this.state = STATES.SECURITY_VIOLATION;
    this._record('SECURITY_VIOLATION', { reason });
    return { allowed: false, state: this.state, reason };
  }

  recommend({ action, target, payload }) {
    if (![STATES.IDLE, STATES.REJECTED].includes(this.state)) {
      return this._violation('invalid_transition_to_recommendation');
    }
    if (typeof action !== 'string' || !action.trim() || typeof target !== 'string' || !target.trim()) {
      return { allowed: false, state: this.state, reason: 'action_and_target_required' };
    }
    this.recommendation = { action, target, payloadHash: sha256(payload ?? null) };
    this.evidence = null;
    this.authorization = null;
    this.state = STATES.RECOMMENDATION;
    this._record('RECOMMENDATION_CREATED', { ...this.recommendation });
    return { allowed: true, state: this.state };
  }

  attachEvidence(evidence) {
    if (this.state !== STATES.RECOMMENDATION) {
      return this._violation('invalid_transition_to_evidence_attached');
    }
    const missing = this.requiredEvidence.filter((key) =>
      evidence == null || evidence[key] === undefined || evidence[key] === null || evidence[key] === ''
    );
    if (missing.length) {
      this._record('EVIDENCE_REJECTED', { missing });
      return { allowed: false, state: this.state, reason: 'required_evidence_missing', missing };
    }
    this.evidence = evidence;
    this.state = STATES.EVIDENCE_ATTACHED;
    this._record('EVIDENCE_ATTACHED', { evidenceHash: sha256(evidence) });
    this.state = STATES.AUTHORIZATION_PENDING;
    this._record('AUTHORIZATION_REQUESTED', { action: this.recommendation.action, target: this.recommendation.target });
    return { allowed: true, state: this.state, evidenceHash: sha256(evidence) };
  }

  createAuthorizationPayload({ nonce = crypto.randomUUID(), expiresAt, approver, action, target } = {}) {
    if (this.state !== STATES.AUTHORIZATION_PENDING || !this.recommendation || !this.evidence) {
      throw new Error('authorization can only be prepared while authorization is pending');
    }
    return {
      version: 1,
      approver,
      action: action ?? this.recommendation.action,
      target: target ?? this.recommendation.target,
      recommendationHash: sha256(this.recommendation),
      evidenceHash: sha256(this.evidence),
      nonce,
      expiresAt
    };
  }

  authorize(payload, signature) {
    if (this.state !== STATES.AUTHORIZATION_PENDING) {
      return this._violation('authorization_outside_pending_state');
    }
    if (!this.publicKey || !payload || typeof signature !== 'string') {
      this._record('AUTHORIZATION_REJECTED', { reason: 'missing_public_key_payload_or_signature' });
      return { allowed: false, state: this.state, reason: 'invalid_authorization_material' };
    }
    let validSignature = false;
    try {
      validSignature = crypto.verify(null, Buffer.from(canonicalJson(payload)), this.publicKey, Buffer.from(signature, 'base64'));
    } catch {
      validSignature = false;
    }
    if (!validSignature) {
      this._record('AUTHORIZATION_REJECTED', { reason: 'invalid_signature' });
      return { allowed: false, state: this.state, reason: 'invalid_signature' };
    }
    if (!Number.isFinite(payload.expiresAt) || payload.expiresAt <= this.clock()) {
      this._record('AUTHORIZATION_REJECTED', { reason: 'expired_or_invalid_expiry' });
      return { allowed: false, state: this.state, reason: 'expired_or_invalid_expiry' };
    }
    if (typeof payload.nonce !== 'string' || !payload.nonce || this.consumedNonces.has(payload.nonce)) {
      this._record('AUTHORIZATION_REJECTED', { reason: 'replayed_or_missing_nonce' });
      return { allowed: false, state: this.state, reason: 'replayed_or_missing_nonce' };
    }
    if (payload.action !== this.recommendation.action ||
        payload.target !== this.recommendation.target ||
        payload.recommendationHash !== sha256(this.recommendation) ||
        payload.evidenceHash !== sha256(this.evidence)) {
      this._record('AUTHORIZATION_REJECTED', { reason: 'authorization_scope_mismatch' });
      return { allowed: false, state: this.state, reason: 'authorization_scope_mismatch' };
    }
    this.consumedNonces.add(payload.nonce);
    this.authorization = { ...payload, signature };
    this.state = STATES.AUTHORIZED;
    this._record('HUMAN_AUTHORIZATION_ACCEPTED', { approver: payload.approver, nonce: payload.nonce });
    return { allowed: true, state: this.state };
  }

  reject({ approver, reason = 'human_rejected' } = {}) {
    if (![STATES.RECOMMENDATION, STATES.EVIDENCE_ATTACHED, STATES.AUTHORIZATION_PENDING].includes(this.state)) {
      return this._violation('rejection_outside_reviewable_state');
    }
    this.state = STATES.REJECTED;
    this._record('HUMAN_REJECTED', { approver, reason });
    return { allowed: true, state: this.state };
  }

  execute() {
    if (this.state !== STATES.AUTHORIZED || !this.authorization) {
      this._record('EXECUTION_BLOCKED', { reason: 'valid_human_authorization_required' });
      return { allowed: false, state: this.state, reason: 'valid_human_authorization_required' };
    }
    if (this.authorization.expiresAt <= this.clock()) {
      this.state = STATES.REJECTED;
      this._record('EXECUTION_BLOCKED', { reason: 'authorization_expired_before_execution' });
      return { allowed: false, state: this.state, reason: 'authorization_expired_before_execution' };
    }
    this.state = STATES.EXECUTING;
    this._record('EXECUTION_GATE_PASSED', { action: this.recommendation.action, target: this.recommendation.target });
    return { allowed: true, state: this.state, action: this.recommendation.action, target: this.recommendation.target };
  }

  complete({ resultHash } = {}) {
    if (this.state !== STATES.EXECUTING) {
      return this._violation('completion_without_execution_gate');
    }
    this.state = STATES.COMPLETED;
    this._record('EXECUTION_COMPLETED', { resultHash: resultHash ?? null });
    return { allowed: true, state: this.state };
  }

  verifyEventChain() {
    let previousHash = 'GENESIS';
    for (const event of this.events) {
      if (event.previousHash !== previousHash) return { valid: false, reason: 'previous_hash_mismatch' };
      const { hash, ...body } = event;
      if (sha256(body) !== hash) return { valid: false, reason: 'event_hash_mismatch' };
      previousHash = hash;
    }
    return { valid: true, eventCount: this.events.length, headHash: previousHash };
  }

  exportAudit() {
    return JSON.parse(JSON.stringify(this.events));
  }
}

module.exports = { HslExecutionGate, STATES, canonicalJson, sha256 };
