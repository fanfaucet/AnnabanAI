"""Client wrapper for the xAI Grok API using the OpenAI-compatible SDK."""


class GrokClient:
    """Thin wrapper around xAI's OpenAI-compatible endpoint."""

    def __init__(self, api_key: str, model: str = "grok-4.20") -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
        self.model = model

    def call(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        """Send a prompt to Grok and return the model text response."""
        completion = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return completion.choices[0].message.content or ""
