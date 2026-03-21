const nacl = require('tweetnacl');
const util = require('tweetnacl-util');

function verifyRelayEnvelope(envelope) {
  const body = JSON.stringify({
    fromNodeId: envelope.fromNodeId,
    toNodeId: envelope.toNodeId,
    ciphertext: envelope.ciphertext,
    nonce: envelope.nonce,
    timestamp: envelope.timestamp
  });

  return nacl.sign.detached.verify(
    util.decodeUTF8(body),
    util.decodeBase64(envelope.signature),
    util.decodeBase64(envelope.fromSignPublicKey)
  );
}

function relayEnvelope(envelope, peersById) {
  if (!verifyRelayEnvelope(envelope)) {
    throw new Error('Relay signature verification failed');
  }

  const target = peersById.get(envelope.toNodeId);
  if (!target) {
    throw new Error('Target peer unavailable');
  }

  return {
    forwardedTo: target.endpoint,
    envelope
  };
}

module.exports = {
  verifyRelayEnvelope,
  relayEnvelope
};
