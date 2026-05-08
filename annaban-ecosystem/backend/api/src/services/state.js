const { v4: uuid } = require('uuid');

const db = {
  sensorEvents: [],
  decisions: [],
  governance: [],
  audit: []
};

function addSensorEvent(event) {
  const item = { id: uuid(), timestamp: new Date().toISOString(), ...event };
  db.sensorEvents.unshift(item);
  db.sensorEvents = db.sensorEvents.slice(0, 250);
  return item;
}

function addDecision(decision) {
  const item = { id: uuid(), timestamp: new Date().toISOString(), status: 'pending_human', ...decision };
  db.decisions.unshift(item);
  db.decisions = db.decisions.slice(0, 250);
  return item;
}

function resolveDecision(id, status, reviewer) {
  const decision = db.decisions.find((d) => d.id === id);
  if (!decision) return null;
  decision.status = status;
  decision.reviewedBy = reviewer;
  decision.reviewedAt = new Date().toISOString();
  db.governance.unshift({ id: uuid(), decisionId: id, status, reviewer, timestamp: decision.reviewedAt });
  return decision;
}

function addAudit(event) {
  db.audit.unshift({ id: uuid(), timestamp: new Date().toISOString(), ...event });
}

module.exports = { db, addSensorEvent, addDecision, resolveDecision, addAudit };
