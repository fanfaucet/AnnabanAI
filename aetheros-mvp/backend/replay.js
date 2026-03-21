const seenMessageIds = new Set();

function enforceReplayProtection(msgId, timestamp, maxDriftMs) {
  if (seenMessageIds.has(msgId)) {
    throw new Error('Replay detected: duplicate msgId');
  }

  const delta = Math.abs(Date.now() - Number(timestamp));
  if (Number.isNaN(delta) || delta > maxDriftMs) {
    throw new Error('Replay detected: timestamp outside drift window');
  }

  seenMessageIds.add(msgId);
}

module.exports = {
  enforceReplayProtection
};
