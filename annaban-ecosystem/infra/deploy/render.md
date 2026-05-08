# Render Deployment

1. Create 5 services from the monorepo:
   - backend/api (Node Web Service)
   - backend/ai (Python Web Service)
   - backend/aether (Python Web Service)
   - backend/oracle (Python Web Service)
   - frontend/dashboard (Static Site or Web Service)
2. Set environment values from `backend/api/.env.example`.
3. For blockchain minting, set `MINT_RPC_URL`, `MINT_PRIVATE_KEY`, and `MINT_CONTRACT` in API service.
4. Configure internal URLs:
   - `PY_AI_URL=http://<ai-internal-url>`
   - `PY_AETHER_URL=http://<aether-internal-url>`
   - `PY_ORACLE_URL=http://<oracle-internal-url>`
