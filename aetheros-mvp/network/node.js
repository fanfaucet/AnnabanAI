const express = require('express');
const nacl = require('tweetnacl');
const util = require('tweetnacl-util');
const config = require('./config.example');
const { registerNode, listNodes } = require('./registry');
const { relayEnvelope } = require('./relay');

const app = express();
app.use(express.json());

const signKeys = nacl.sign.keyPair();
const boxKeys = nacl.box.keyPair();
const peersById = new Map();

function localIdentity() {
  return {
    nodeId: config.nodeId,
    endpoint: config.endpoint,
    boxPublicKey: util.encodeBase64(boxKeys.publicKey),
    signPublicKey: util.encodeBase64(signKeys.publicKey),
    timestamp: Date.now()
  };
}

function signIdentity(identity) {
  const body = JSON.stringify(identity);
  const sig = nacl.sign.detached(util.decodeUTF8(body), signKeys.secretKey);
  return util.encodeBase64(sig);
}

app.get('/health', (_req, res) => {
  res.json({ ok: true, nodeId: config.nodeId });
});

app.get('/nodes', (_req, res) => {
  res.json({ nodes: listNodes() });
});

app.post('/register', (req, res) => {
  try {
    const { identity, signature } = req.body;
    const nodes = registerNode(identity, signature);
    peersById.set(identity.nodeId, identity);
    res.json({ ok: true, nodes });
  } catch (error) {
    res.status(400).json({ ok: false, error: error.message });
  }
});

app.post('/relay', (req, res) => {
  try {
    const forwarded = relayEnvelope(req.body, peersById);
    res.json({ ok: true, forwarded });
  } catch (error) {
    res.status(400).json({ ok: false, error: error.message });
  }
});

app.post('/bootstrap', (_req, res) => {
  const identity = localIdentity();
  const signature = signIdentity(identity);
  const nodes = registerNode(identity, signature);
  res.json({ ok: true, identity, nodes });
});

app.listen(config.port, () => {
  console.log(`AetherOS network node listening at ${config.endpoint}`);
});
