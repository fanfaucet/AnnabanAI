const seen = new Set();

function isReplay(msgId) {
  if (seen.has(msgId)) {
    return true;
  }

  seen.add(msgId);
  return false;
}

function withinDrift(timestamp, maxSkewMs = 30_000) {
  const now = Date.now();
  return Math.abs(now - Number(timestamp)) <= maxSkewMs;
}

module.exports = {
  isReplay,
  withinDrift
};
