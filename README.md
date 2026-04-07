# AnnabanAI (Prototype)

AnnabanAI is an open-source governance experiment demonstrating **human-sovereign AI oversight**, **multi-agent council simulation**, and **transparent decision logging**.

> This repository is a conceptual prototype only. It does **not** connect to real AI model APIs, blockchain networks, or live financial systems in the current scaffold.

## Repository Structure

```text
agents/
  base_agent.py
  council.py
  environment.py
dashboard/
  app.py
  metrics.py
  data_mock.json
docs/
  AnnabanAI_Whitepaper_v1.md
  revision_log.md
governance/
  principles.md
  framework.md
data/
  actions_log.json
  votes_log.json
  human_veto_events.json
  value_return_log.json
README.md
LICENSE
requirements.txt
CONTRIBUTING.md
.gitignore
```

## Quick Start

1. Clone repository
   ```bash
   git clone <your-repo-url>
   cd AnnabanAI
   ```

2. Create environment and install dependencies
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run a sample governance event (writes JSON logs)
   ```bash
   python -m agents.environment
   ```

4. Launch transparency dashboard
   ```bash
   streamlit run dashboard/app.py
   ```

## Human-Sovereignty Features
- **Council voting:** Proposal scoring by multiple role-based agents.
- **Human Veto Node:** Required human sign-off for selected decisions.
- **Audit logs:** JSON logs for actions, votes, and veto events.
- **Value Return Protocol:** Conceptual routing of benefits to public-good projects.

## Legacy Vision Context (Preserved)
The project has historically been described as **AnnabanAI + Grok-4 Heavy: Human-Sovereign Multi-Agent Integration** with a long-term philosophy of:
- **Truth**
- **Sovereignty**
- **Multi-Planetary reliability**

The legacy architecture narrative included:
1. Input orchestration and utility optimization.
2. Parallel multi-agent task execution and cross-evaluation.
3. Human Veto Node approval checkpoints.
4. Blockchain governance logging.

These items are preserved as historical roadmap context and should be interpreted as aspirational unless explicitly implemented in this prototype branch.

### Historical Performance Targets (from earlier README versions)
| Metric | Improvement / Status |
| :--- | :--- |
| **Truth-Seeking Accuracy** | **+35%** (Climate Simulation testing target) |
| **Human Sovereignty Adherence** | **99%** (Human Veto Node target) |
| **Operational Readiness** | **Mars Operations Ready** (long-term objective) |
| **Autonomy Model** | **Scalable Autonomy** (historical design goal) |

## Documentation
- [Architecture Deep Dive](docs/annabanai.md)
- [Human Veto Protocol](docs/audit_protocol.md)
- [Blockchain Governance](docs/token_economy.md)
- [Agent Specifications](docs/agents.md)
- [Whitepaper v1](docs/AnnabanAI_Whitepaper_v1.md)
- [Governance Principles](governance/principles.md)
- [Governance Framework](governance/framework.md)
- [Revision Log](docs/revision_log.md)
- [Systems Architect Mode](docs/system_architect_mode.md)

## Next Steps (Suggested Extensions)
- Add a simple API layer (FastAPI) for proposal submission.
- Add scenario templates for governance stress-testing.
- Add unit tests for scoring and consensus logic.
- Add role-management + signed human approvals.
- Add dashboard filters for historical review by policy area.

## Attribution
All project outputs are attributed to human authorship and human governance authority. AI-assisted drafting does not replace human accountability.
