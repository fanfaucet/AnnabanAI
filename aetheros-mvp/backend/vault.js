const nacl = require('tweetnacl');
const util = require('tweetnacl-util');

const serverBoxKeyPair = nacl.box.keyPair();
const serverSignKeyPair = nacl.sign.keyPair();

module.exports = {
  boxPublicKeyB64: util.encodeBase64(serverBoxKeyPair.publicKey),
  boxSecretKey: serverBoxKeyPair.secretKey,
  signPublicKeyB64: util.encodeBase64(serverSignKeyPair.publicKey),
  signSecretKey: serverSignKeyPair.secretKey
};
