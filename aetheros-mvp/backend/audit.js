const crypto = require('crypto');
const fs = require('fs');

function computeHash(entry, prevHash) {
  const materialized = JSON.stringify({ ...entry, prevHash });
  return crypto.createHash('sha256').update(materialized).digest('hex');
}

function readLedger(ledgerPath) {
  if (!fs.existsSync(ledgerPath)) {
    return [];
  }

  const content = fs.readFileSync(ledgerPath, 'utf8').trim();
  if (!content) {
    return [];
  }

  return content
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}

function appendLedgerEntry(ledgerPath, entryInput) {
  const ledger = readLedger(ledgerPath);
  const prevHash = ledger.length ? ledger[ledger.length - 1].hash : 'GENESIS';

  const entry = {
    timestamp: entryInput.timestamp,
    msgId: entryInput.msgId,
    direction: entryInput.direction,
    payload: entryInput.payload,
    prevHash
  };

  const hash = computeHash(entry, prevHash);
  const committed = { ...entry, hash };
  fs.appendFileSync(ledgerPath, `${JSON.stringify(committed)}\n`);
  return committed;
}

function verifyLedger(ledgerPath) {
  const ledger = readLedger(ledgerPath);
  let expectedPrevHash = 'GENESIS';

  for (const entry of ledger) {
    if (entry.prevHash !== expectedPrevHash) {
      return {
        valid: false,
        reason: `prevHash mismatch for msgId ${entry.msgId}`
      };
    }

    const recalculated = computeHash(
      {
        timestamp: entry.timestamp,
        msgId: entry.msgId,
        direction: entry.direction,
        payload: entry.payload,
        prevHash: entry.prevHash
      },
      entry.prevHash
    );

    if (recalculated !== entry.hash) {
      return {
        valid: false,
        reason: `hash mismatch for msgId ${entry.msgId}`
      };
    }

    expectedPrevHash = entry.hash;
  }

  return { valid: true, reason: 'Ledger chain is valid' };
}

module.exports = {
  appendLedgerEntry,
  verifyLedger
};
