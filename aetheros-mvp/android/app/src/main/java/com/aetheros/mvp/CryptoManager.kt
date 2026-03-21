package com.aetheros.mvp

import com.goterl.lazysodium.LazySodiumAndroid
import com.goterl.lazysodium.SodiumAndroid
import com.goterl.lazysodium.interfaces.Box
import com.goterl.lazysodium.interfaces.Sign
import com.google.gson.Gson
import java.util.Base64
import java.util.UUID

class CryptoManager {
    private val sodium = LazySodiumAndroid(SodiumAndroid())
    private val gson = Gson()

    private val boxKeyPair = Box.KeyPair()
    private val signKeyPair = Sign.KeyPair()

    init {
        sodium.cryptoBoxKeypair(boxKeyPair)
        sodium.cryptoSignKeypair(signKeyPair)
    }

    fun clientBoxPublicKey(): String = Base64.getEncoder().encodeToString(boxKeyPair.publicKey.asBytes)
    fun clientSignPublicKey(): String = Base64.getEncoder().encodeToString(signKeyPair.publicKey.asBytes)

    fun buildEncryptedRequest(intent: String, serverBoxPublicKeyB64: String): EncryptedRequest {
        val messageObj = mapOf("intent" to intent)
        val plaintext = gson.toJson(messageObj)

        val signature = ByteArray(Sign.BYTES)
        sodium.cryptoSignDetached(signature, plaintext.toByteArray(), plaintext.length.toLong(), signKeyPair.secretKey)

        val envelope = mapOf(
            "msgId" to UUID.randomUUID().toString(),
            "timestamp" to System.currentTimeMillis(),
            "message" to messageObj,
            "signature" to Base64.getEncoder().encodeToString(signature),
            "clientSignPublicKey" to clientSignPublicKey()
        )

        val envelopeString = gson.toJson(envelope)
        val nonce = ByteArray(Box.NONCEBYTES)
        sodium.randomBuf(nonce, nonce.size)
        val cipher = ByteArray(envelopeString.toByteArray().size + Box.MACBYTES)

        sodium.cryptoBoxEasy(
            cipher,
            envelopeString.toByteArray(),
            envelopeString.toByteArray().size.toLong(),
            nonce,
            Base64.getDecoder().decode(serverBoxPublicKeyB64),
            boxKeyPair.secretKey.asBytes
        )

        return EncryptedRequest(
            clientBoxPublicKey = clientBoxPublicKey(),
            nonce = Base64.getEncoder().encodeToString(nonce),
            ciphertext = Base64.getEncoder().encodeToString(cipher)
        )
    }

    fun decryptAndVerifyResponse(
        encryptedResponse: EncryptedResponse,
        serverBoxPublicKeyB64: String,
        serverSignPublicKeyB64: String
    ): Pair<String, Boolean> {
        val nonce = Base64.getDecoder().decode(encryptedResponse.nonce)
        val cipher = Base64.getDecoder().decode(encryptedResponse.ciphertext)
        val plain = ByteArray(cipher.size - Box.MACBYTES)

        val opened = sodium.cryptoBoxOpenEasy(
            plain,
            cipher,
            cipher.size.toLong(),
            nonce,
            Base64.getDecoder().decode(serverBoxPublicKeyB64),
            boxKeyPair.secretKey.asBytes
        )

        if (!opened) {
            return Pair("Unable to decrypt server response", false)
        }

        val payload = String(plain)
        val obj = gson.fromJson(payload, Map::class.java)
        val message = gson.toJson(obj["message"])
        val signature = Base64.getDecoder().decode(obj["signature"].toString())

        val verified = sodium.cryptoSignVerifyDetached(
            signature,
            message.toByteArray(),
            message.toByteArray().size.toLong(),
            Base64.getDecoder().decode(serverSignPublicKeyB64)
        )

        return Pair(message, verified)
    }
}
