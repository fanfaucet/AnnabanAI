# AnnabanAI Research Index

**Purpose:** reduce time spent locating implementation evidence and make research claims auditable.
**Repository:** `fanfaucet/AnnabanAI`
**Index status:** manually assembled from the repository tree and file contents reviewed on 2026-10-28. This file is a navigation aid, not an automated inventory or certification.

## Start here

| Research question | Entry point | Evidence status |
|---|---|---|
| What does this repository claim to be? | [README.md](README.md) | Project description; includes conceptual and aspirational material |
| What is the broad model/system specification? | [ChatGPT AI System Specification](docs/ChatGPT_AI_System_Specification.md) | Design document, not proof that described capabilities exist |
| Where is the existing AnnabanOS ↔ AnnabanAI bridge API? | [backend API](annaban-ecosystem/backend/api/main.py) | Existing implementation file; endpoints and dependencies still require runtime testing |
| Where is the AI service? | [AI service](annaban-ecosystem/backend/ai/main.py) | Existing implementation file; inspect before extending |
| Where is the AetherOS simulation service? | [AetherOS service](annaban-ecosystem/backend/aether/main.py) | Simulation-oriented implementation |
| Where are agent orchestration examples? | [agents/](agents/) | Source and tests; test status depends on CI/run evidence |
| Where is the new chat API scaffold? | [annaban_llm/README.md](annaban_llm/README.md) | Implemented on feature branch; not yet production-validated |
| Where are chat API contract tests? | [test_api_server.py](annaban_llm/test_api_server.py) | Test source exists; passing status requires an actual test run |

## New chat API scaffold

- [API implementation](annaban_llm/api_server.py)
- [Endpoint and security notes](annaban_llm/README.md)
- [Contract tests](annaban_llm/test_api_server.py)
- [Isolated dependencies](annaban_llm/requirements.txt)

Implemented endpoints: `/health`, `/api/v1/chat/completions`, `/api/v1/chat/stream`, `/api/v1/chat/tempo-modes`, `/api/v1/chat/feedback`, and `/api/v1/covenant`.

Important limits: generation requires runtime provider credentials; feedback is not persisted; scores are unmeasured/null; covenant compliance is not asserted; provenance is descriptive and not cryptographically signed. See the package README before deployment.

## Evidence labels

Use these labels in issues, pull requests, benchmarks, and future documentation:

1. **PROPOSED** — a requirement, idea, or roadmap item.
2. **DOCUMENTED** — written in repository documentation, without proof of runtime behavior.
3. **IMPLEMENTED** — corresponding source code exists.
4. **TESTED** — a reproducible test was run and its result is recorded.
5. **INDEPENDENTLY VERIFIED** — evidence was checked by a separate process or reviewer with method and scope recorded.

Do not promote a claim from one tier to another without new evidence. A source file is not a passing test; a passing unit test is not a production deployment; a generated answer is not independently verified.

## Research workflow

For each feature or claim, record:

- **Claim:** one testable sentence.
- **Location:** file, symbol, endpoint, or commit.
- **Evidence tier:** one of the labels above.
- **Verification method:** exact command, test case, review procedure, or external source.
- **Result:** pass/fail/not run, including date and environment.
- **Limitations:** what the evidence does not establish.
- **Next step:** the smallest action that would improve confidence.

Suggested commands from the repository root:

```bash
# Search source and documentation
grep -RIn --exclude-dir=.git "search phrase" .

# Run the existing agent tests (requires the project's Python dependencies)
pytest -q agents

# Run the chat API contract tests (install annaban_llm/requirements.txt first)
pytest -q annaban_llm/test_api_server.py
```

These commands are suggested workflows, not a claim that tests have already passed.

## Review queue

- [ ] Add this index to future feature PRs when they introduce a new subsystem.
- [ ] Add CI that runs relevant tests and publishes the exact result.
- [ ] Link each API endpoint to request/response models and tests.
- [ ] Define stable meanings for terms such as `verified`, `confidence`, `empathy_score`, and `covenant_aligned` before exposing them as factual metadata.
- [ ] Keep generated content, user assertions, simulation output, and independently verified external facts visibly distinct.
