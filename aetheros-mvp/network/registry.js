const nacl = require('tweetnacl');
const util = require('tweetnacl-util');

const nodes = new Map();

function canonicalIdentity(identity) {
  return JSON.stringify({
    nodeId: identity.nodeId,
    endpoint: identity.endpoint,
    boxPublicKey: identity.boxPublicKey,
    signPublicKey: identity.signPublicKey,
    timestamp: identity.timestamp
  });
}

function registerNode(identity, signatureB64) {
  const ok = nacl.sign.detached.verify(
    util.decodeUTF8(canonicalIdentity(identity)),
    util.decodeBase64(signatureB64),
    util.decodeBase64(identity.signPublicKey)
  );

  if (!ok) {
    throw new Error('Invalid node identity signature');
  }

  nodes.set(identity.nodeId, { ...identity, signature: signatureB64 });
  return Array.from(nodes.values());
}

function listNodes() {
  return Array.from(nodes.values());
}

module.exports = {
  registerNode,
  listNodes
};
