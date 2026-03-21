require('dotenv').config();
const express = require('express');
const path = require('path');
const { decryptPayload, encryptResponse } = require('./crypto');
const { verifyClientSignature, signServerMessage } = require('./sign');
const { boxPublicKeyB64, signPublicKeyB64 } = require('./vault');
const { isReplay, withinDrift } = require('./replay');
const { appendLedgerEntry, verifyLedger } = require('./audit');

const app = express();
const port = Number(process.env.PORT || 3000);
const maxDriftMs = Number(process.env.MAX_DRIFT_MS || 30000);
const ledgerPath = path.resolve(process.env.LEDGER_PATH || './heritage_ledger.log');

app.use(express.json({ limit: '1mb' }));

const auditStatus = verifyLedger(ledgerPath);
if (!auditStatus.ok) {
  console.error('Startup audit failed:', auditStatus);
  process.exit(1);
}

function resolveIntent(intent) {
  switch (intent) {
    case 'time':
      return { intent, value: new Date().toISOString() };
    case 'status':
      return { intent, value: 'AetherOS backend operational' };
    default:
      return { intent, value: 'Unknown intent' };
  }
}

app.get('/pubkey', (_req, res) => {
  res.json({
    serverBoxPublicKey: boxPublicKeyB64,
    serverSignPublicKey: signPublicKeyB64
  });
});

app.post('/message', (req, res) => {
  try {
    const decrypted = decryptPayload(req.body);
    const plaintext = JSON.stringify(decrypted.message);

    const signatureOk = verifyClientSignature(
      plaintext,
      decrypted.signature,
      decrypted.clientSignPublicKey
    );

    if (!signatureOk) {
      return res.status(401).json({ error: 'Invalid client signature' });
    }

    if (isReplay(decrypted.msgId)) {
      return res.status(409).json({ error: 'Replay detected: duplicate msgId' });
    }

    if (!withinDrift(decrypted.timestamp, maxDriftMs)) {
      return res.status(400).json({ error: 'Replay detected: timestamp outside drift window' });
    }

    const processed = resolveIntent(decrypted.message.intent);
    const responseMessage = {
      msgId: decrypted.msgId,
      requestTimestamp: decrypted.timestamp,
      responseTimestamp: Date.now(),
      result: processed
    };

    appendLedgerEntry(ledgerPath, {
      timestamp: new Date().toISOString(),
      msgId: decrypted.msgId,
      direction: 'request-response',
      payload: responseMessage
    });

    const responsePlaintext = JSON.stringify(responseMessage);
    const signed = signServerMessage(responsePlaintext);

    const encrypted = encryptResponse(
      {
        message: responseMessage,
        signature: signed.signature,
        serverSignPublicKey: signed.serverSignPublicKey
      },
      req.body.clientBoxPublicKey
    );

    return res.json(encrypted);
  } catch (error) {
    return res.status(400).json({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`AetherOS backend listening on port ${port}`);
});
