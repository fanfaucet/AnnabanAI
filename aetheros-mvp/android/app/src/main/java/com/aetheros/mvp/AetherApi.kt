package com.aetheros.mvp

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface AetherApi {
    @GET("pubkey")
    suspend fun getPubkey(): Response<PublicKeyResponse>

    @POST("message")
    suspend fun sendMessage(@Body payload: EncryptedRequest): Response<EncryptedResponse>
}
