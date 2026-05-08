# AnnabanAI Ecosystem — Human-Sovereign Multi-Agent Orchestration Platform

Production-ready reference platform spanning:
- **AnnabanOS** control plane (`backend/api`)
- **AnnabanAI** orchestration (`backend/ai`)
- **AetherOS** simulation (`backend/aether`)
- **OracleOS** knowledge layer (`backend/oracle`)
- **Dashboard UI** (`frontend/dashboard`)
- **Blockchain audit** (`backend/blockchain`)

## Architecture (ASCII)

```text
[Sensors/MQTT] --> [AnnabanOS API] --> [AnnabanAI Agents]
                         |                |  |  |  |
                         |                |  |  |  +--> OracleAgent (context)
                         |                |  |  +-----> SystemAgent (safety)
                         |                |  +--------> AnnabanAgent (ethics)
                         |                +-----------> GrokAgent (fast logic)
                         |
                         +--> [AetherOS Simulation]
                         +--> [OracleOS Reasoning]
                         +--> [Human Governance Approve/Reject]
                         +--> [Polygon Decision NFT Audit Log]
```

## Quick start (local)

```bash
cd annaban-ecosystem/infra
docker compose up
```

UI: http://localhost:5173
API Docs: http://localhost:4000/api-docs

## Manual service startup

1. Start AI services (ports 8001/8002/8003) with uvicorn.
2. Start API:
   ```bash
   cd backend/api
   cp .env.example .env
   npm install
   npm run dev
   ```
3. Start dashboard:
   ```bash
   cd frontend/dashboard
   npm install
   npm run dev
   ```

## Governance workflow

1. Operator requests recommendation (`POST /decisions/recommend`).
2. System sets `requires_human: true` for all decisions.
3. Governor approves/rejects via `/governance/:id/approve|reject`.
4. Approved decision optionally mints Polygon NFT audit record.

## Blockchain logging

Each approved decision records:
- `decision_hash`
- `timestamp`
- `confidence`
- `ethical_score`

Smart contract: `backend/blockchain/contracts/DecisionNFT.sol`


## Using with ChatGPT

You can use the platform with ChatGPT either as an advisory governance copilot or through Custom GPT Actions.

- Quick guide: `docs/chatgpt-usage.md`
- Key rule: ChatGPT should **never** autonomously approve actions; human approval is always required.

## Deployment

- Docker Compose for local full stack (`infra/docker-compose.yml`)
- Render guide (`infra/deploy/render.md`)
- GitHub Actions CI (`infra/github/workflows/ci.yml`)
