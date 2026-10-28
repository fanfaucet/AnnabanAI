# AnnabanAI Chat API scaffold

This package implements a small FastAPI surface for the supplied AnnabanAI chat API design. It is an integration scaffold; it does not claim production readiness, a configured model, or independently certified covenant compliance.

## Endpoints

| Method | Path | Behavior |
|---|---|---|
| GET | `/health` | Health and provider-configuration status; no secrets returned |
| POST | `/api/v1/chat/completions` | Non-streaming chat completion |
| POST | `/api/v1/chat/stream` | Server-Sent Events stream; emits `data: {"delta":"..."}` and `data: [DONE]` |
| GET | `/api/v1/chat/tempo-modes` | Lists concise, balanced, and reflective modes |
| POST | `/api/v1/chat/feedback` | Validates feedback and acknowledges receipt without persistence |
| GET | `/api/v1/covenant` | Returns published governance principles and their implementation caveat |

### Request

```json
{
  "messages": [{"role": "user", "content": "Help me compare two options."}],
  "tempo_mode": "balanced",
  "preserve_agency": true,
  "max_tokens": 800,
  "temperature": 0.2,
  "conversation_id": "optional-client-id"
}
```

### Metadata semantics

- `empathy_score`, `sentiment`, `cognitive_load`, and benefit-vector values are `null` because no validated measurement method is implemented.
- `covenant_aligned` is `null` until an explicit evaluation process exists. Prompting with principles is not proof of compliance.
- Provenance records the response identifier, UTC creation time, provider label, model name, and status `generated_not_independently_verified`. This is descriptive metadata, not a signed or tamper-evident audit trail.
- Conversation content is not logged or persisted by this module. Feedback is acknowledged but not stored.
- If `ANNABAN_API_KEY` is set, endpoints other than `/health` require `Authorization: Bearer <key>`. This single shared key is a prototype gate, not user identity or role-based authorization.

## Run locally

From the repository root:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r annaban_llm/requirements.txt
export OPENAI_API_KEY="your-provider-key"
export ANNABAN_MODEL="gpt-4o-mini"
# Optional: require bearer auth on API routes
export ANNABAN_API_KEY="replace-with-a-long-random-secret"
uvicorn annaban_llm.api_server:app --host 127.0.0.1 --port 8000
```

The model key is supplied at runtime; do not commit credentials or bake them into a container image. For an OpenAI-compatible provider, optionally set `OPENAI_BASE_URL`.

OpenAPI docs are available at `/docs`. If no `OPENAI_API_KEY` is configured, health and descriptive endpoints still work while chat generation returns HTTP 503.

## Tests

```bash
pytest -q annaban_llm/test_api_server.py
```

Tests use a fake model client for the success path and do not call an external model provider.

## Before production

1. Replace the shared optional API key with identity-aware authentication, authorization, quotas, and rate limits.
2. Add persistent feedback only with an explicit retention policy, consent, deletion handling, and access controls.
3. Define and validate measurement protocols before emitting psychological or benefit scores.
4. Add signed audit events if tamper evidence is required; current provenance IDs are not signatures.
5. Review CORS, TLS, secret management, abuse controls, provider data handling, and error monitoring.
6. Run CI in GitHub Actions and verify against the target deployment environment.

## Source attribution

The endpoint concepts and metadata fields originate in a user-supplied, Grok-attributed design artifact. This implementation is a new scaffold based on those supplied requirements; the supplied attribution does not independently verify authorship by Grok or prior implementation.
