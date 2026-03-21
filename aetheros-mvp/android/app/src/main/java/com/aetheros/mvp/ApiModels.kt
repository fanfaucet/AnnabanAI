package com.aetheros.mvp

data class PublicKeyResponse(
    val serverBoxPublicKey: String,
    val serverSignPublicKey: String
)

data class EncryptedRequest(
    val clientBoxPublicKey: String,
    val nonce: String,
    val ciphertext: String
)

data class EncryptedResponse(
    val nonce: String,
    val ciphertext: String
)
