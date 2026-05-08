const nacl = require('tweetnacl');
const util = require('tweetnacl-util');
const { boxSecretKey } = require('./vault');

function decryptPayload(payload) {
  const {
    clientBoxPublicKey,
    nonce,
    ciphertext
  } = payload;

  const opened = nacl.box.open(
    util.decodeBase64(ciphertext),
    util.decodeBase64(nonce),
    util.decodeBase64(clientBoxPublicKey),
    boxSecretKey
  );

  if (!opened) {
    throw new Error('Failed to decrypt payload');
  }

  return JSON.parse(util.encodeUTF8(opened));
}

function encryptResponse(responseObject, clientBoxPublicKey) {
  const nonce = nacl.randomBytes(nacl.box.nonceLength);
  const message = util.decodeUTF8(JSON.stringify(responseObject));

  const encrypted = nacl.box(
    message,
    nonce,
    util.decodeBase64(clientBoxPublicKey),
    boxSecretKey
  );

  return {
    nonce: util.encodeBase64(nonce),
    ciphertext: util.encodeBase64(encrypted)
  };
}

module.exports = {
  decryptPayload,
  encryptResponse
};
