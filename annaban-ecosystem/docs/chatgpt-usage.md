# Using AnnabanAI Ecosystem in ChatGPT

This guide explains two practical ways to use the platform with ChatGPT.

## Option A: Use ChatGPT as a human governance console (fastest)

1. Start the stack:
   ```bash
   cd annaban-ecosystem/infra
   docker compose up
   ```
2. In ChatGPT, paste your current sensor/operational context and ask ChatGPT to prepare an operator request.
3. Use the API endpoints manually (Postman/curl) while ChatGPT helps interpret outcomes:
   - `POST /auth/login`
   - `POST /sensors/ingest`
   - `POST /decisions/recommend`
   - `POST /governance/:id/approve` or `.../reject`
4. Keep final authority with human approvers. The platform enforces `requires_human: true` for recommendations.

## Option B: Connect as a Custom GPT Action (recommended for demos)

Use ChatGPT Custom GPT Actions to call the Annaban API directly.

### 1) Expose API with HTTPS
- Deploy API service (Render/AWS) or tunnel local API with a secure URL.
- Ensure these endpoints are reachable:
  - `https://<your-api>/auth/login`
  - `https://<your-api>/sensors/ingest`
  - `https://<your-api>/decisions/recommend`
  - `https://<your-api>/governance/{id}/approve`
  - `https://<your-api>/governance/{id}/reject`

### 2) Create a Custom GPT
- In ChatGPT, create a new GPT.
- Add Action(s) using your OpenAPI schema (you can generate from API routes or maintain a small static spec).
- Configure auth header handling (Bearer token from `/auth/login`).

### 3) Suggested GPT instruction
Use this system instruction style:
- "You are an Annaban governance copilot. You can summarize sensor data and retrieve recommendations, but you must never execute autonomous actions. Every operational recommendation requires explicit human approval."

### 4) Safe prompt examples
- "Fetch latest sensor state and propose the safest action with explanation."
- "Create a recommendation and list ethical tradeoffs before any approval."
- "Prepare an approval briefing for decision `<id>` including confidence, ethical score, and risks."

## Governance policy for ChatGPT usage

- ChatGPT is advisory only.
- Never auto-call approval endpoints without explicit user command.
- Always return explainability bullets and risk caveats.
- Require a human sign-off statement in operator workflows.

## Example curl flow ChatGPT can guide

```bash
# 1) Login
curl -s -X POST http://localhost:4000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2) Ingest sensor event
curl -s -X POST http://localhost:4000/sensors/ingest \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"source":"simulator","metric":"load_index","value":82.7,"unit":"index","location":"Plant-A"}'

# 3) Request recommendation
curl -s -X POST http://localhost:4000/decisions/recommend \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Balance efficiency and safety"}'

# 4) Human approves/rejects
curl -s -X POST http://localhost:4000/governance/<DECISION_ID>/approve \
  -H "Authorization: Bearer <TOKEN>"
```

## Enterprise tip
For investor/client demos, pair the Dashboard with ChatGPT narration:
1. ChatGPT summarizes incoming telemetry.
2. ChatGPT explains recommended actions and ethics.
3. Human operator performs explicit approve/reject action.
4. Show blockchain audit entry for approved decisions.
