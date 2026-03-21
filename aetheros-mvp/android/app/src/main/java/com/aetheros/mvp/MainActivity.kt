package com.aetheros.mvp

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class MainActivity : AppCompatActivity() {
    private val baseUrl = "http://10.0.2.2:3000/"
    private val cryptoManager = CryptoManager()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val input = findViewById<EditText>(R.id.inputIntent)
        val button = findViewById<Button>(R.id.sendButton)
        val response = findViewById<TextView>(R.id.responseText)
        val badge = findViewById<TextView>(R.id.verificationBadge)

        val api = Retrofit.Builder()
            .baseUrl(baseUrl)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(AetherApi::class.java)

        button.setOnClickListener {
            val intentValue = input.text.toString().ifBlank { "status" }
            lifecycleScope.launch {
                try {
                    val pubkeys = withContext(Dispatchers.IO) { api.getPubkey() }.body()
                        ?: error("Missing server keys")

                    val payload = cryptoManager.buildEncryptedRequest(intentValue, pubkeys.serverBoxPublicKey)
                    val encryptedResponse = withContext(Dispatchers.IO) {
                        api.sendMessage(payload)
                    }.body() ?: error("Missing encrypted response")

                    val (message, verified) = cryptoManager.decryptAndVerifyResponse(
                        encryptedResponse,
                        pubkeys.serverBoxPublicKey,
                        pubkeys.serverSignPublicKey
                    )

                    response.text = message
                    badge.text = if (verified) "🛡️ Verified" else "⚠️ Unverified"
                } catch (e: Exception) {
                    response.text = "Error: ${e.message}"
                    badge.text = "⚠️ Unverified"
                }
            }
        }
    }
}
