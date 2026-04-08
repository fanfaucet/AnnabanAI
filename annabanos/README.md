# AnnabanOS

AnnabanOS is a governance-first AI prototype that wraps the xAI Grok API with a policy enforcement layer, human approval gate, and append-only audit ledger.

## Features

- xAI Grok integration via OpenAI-compatible endpoint (`https://api.x.ai/v1`)
- Governance layer (`AnnabanGovernance`) for policy checks
- High-risk action detection (`deploy`, `execute`, `run`, `activate`)
- Human-in-the-loop gating requiring approval from **Jacob Kinnaird**
- JSONL ledger for full interaction auditability
- Dictionary-based tool-calling with `verify_origin`
- Dual-agent example (Planner + Oversight)

## Repository Layout

```text
annabanos/
├── README.md
├── requirements.txt
├── .env.example
├── main.py
├── annaban/
│   ├── __init__.py
│   ├── grok_client.py
│   ├── governance.py
│   ├── tools.py
│   └── ledger.py
├── examples/
│   └── dual_agent_demo.py
├── logs/
│   └── governance_ledger.jsonl
└── docs/
    └── AnnabanAI_Whitepaper.md
```

## Quick Start

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment:

   ```bash
   cp .env.example .env
   # edit .env and set XAI_API_KEY
   ```

3. Run CLI:

   ```bash
   python main.py
   ```

4. Run dual-agent demo:

   ```bash
   python examples/dual_agent_demo.py
   ```

## Governance Flow

1. User prompt enters `AnnabanGovernance`.
2. Prompt is checked for high-risk keywords.
3. If flagged, the system returns:
   `⚠️ HUMAN APPROVAL REQUIRED FROM Jacob Kinnaird BEFORE EXECUTION`
4. If not flagged, the prompt is sent to Grok (`grok-4.20`).
5. Every interaction is written to `logs/governance_ledger.jsonl`.
