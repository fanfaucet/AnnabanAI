const nacl = require('tweetnacl');
const util = require('tweetnacl-util');
const { signSecretKey, signPublicKeyB64 } = require('./vault');

function verifyClientSignature(plaintext, signatureB64, clientSignPublicKeyB64) {
  return nacl.sign.detached.verify(
    util.decodeUTF8(plaintext),
    util.decodeBase64(signatureB64),
    util.decodeBase64(clientSignPublicKeyB64)
  );
}

function signServerMessage(plaintext) {
  const sig = nacl.sign.detached(
    util.decodeUTF8(plaintext),
    signSecretKey
  );

  return {
    signature: util.encodeBase64(sig),
    serverSignPublicKey: signPublicKeyB64
  };
}

module.exports = {
  verifyClientSignature,
  signServerMessage
};
