const crypto = require('crypto');
const fs = require('fs');

function sha256(value) {
  return crypto.createHash('sha256').update(value).digest('hex');
}

function readLedger(ledgerPath) {
  if (!fs.existsSync(ledgerPath)) {
    return [];
  }

  const raw = fs.readFileSync(ledgerPath, 'utf8').trim();
  if (!raw) {
    return [];
  }

  return raw
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}

function appendLedgerEntry(ledgerPath, entryInput) {
  const ledger = readLedger(ledgerPath);
  const prevHash = ledger.length ? ledger[ledger.length - 1].hash : null;

  const entry = {
    timestamp: entryInput.timestamp,
    msgId: entryInput.msgId,
    direction: entryInput.direction,
    payload: entryInput.payload,
    prevHash
  };

  const hash = sha256(JSON.stringify(entry) + (entry.prevHash || ''));
  const committed = { ...entry, hash };
  fs.appendFileSync(ledgerPath, `${JSON.stringify(committed)}\n`);
  return committed;
}

function verifyLedger(ledgerPath = './heritage_ledger.log') {
  const ledger = readLedger(ledgerPath);
  let prevHash = null;

  for (let i = 0; i < ledger.length; i += 1) {
    const entry = ledger[i];
    const clone = { ...entry };
    const storedHash = clone.hash;
    delete clone.hash;

    const recomputed = sha256(JSON.stringify(clone) + (clone.prevHash || ''));

    if (entry.prevHash !== prevHash) {
      return { ok: false, reason: 'prevHash mismatch', at: i };
    }

    if (storedHash !== recomputed) {
      return { ok: false, reason: 'hash mismatch', at: i };
    }

    prevHash = storedHash;
  }

  return { ok: true, lastHash: prevHash, count: ledger.length };
}

module.exports = {
  readLedger,
  appendLedgerEntry,
  verifyLedger
};
