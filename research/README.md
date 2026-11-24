# AnnabanAI Frontier Orchestration Research Prototype

**Originating architect / project attribution:** Jacob Wayne Kinnaird  
**Status:** Research prototype; simulation-first; not production-certified  
**Authority:** Advisory only. Human authorization required for external effects.  
**External effects by default:** None.

This directory documents a public research path for a multi-agent coordinator, creative/multimodal delegation, and a provenance-aware shared portfolio.

## Research goals

1. Decompose a human request into bounded, typed tasks.
2. Run independent analysis and code tasks concurrently where dependencies permit.
3. Route creative work through a provider adapter rather than hard-coding a vendor SDK into the coordinator.
4. Preserve provenance: user request, task plan, provider/model identity, outputs, review state, and timestamps.
5. Store portfolio entries locally as JSON Lines by default; remote Firebase publishing must be explicitly configured and authorized.
6. Keep the coordinator advisory: it must not silently alter the human's request, deploy code, fly drones, or publish externally.

## Burkburnett heat-mitigation scenario

The example scenario asks for a conceptual solar-shading drone network and a visual prototype over a generic 1920s bungalow in Burkburnett, Texas. It is a **desktop research simulation**, not an engineering design or operational authorization. It does not provide validated thermal calculations, airspace clearance, flight plans, structural assessments, or public-safety approvals. No real drone control is implemented.

## Architecture

- **Decomposer:** turns a request into explicit task records.
- **Delegation router:** maps task types to injected agent adapters.
- **Concurrent runner:** executes only tasks whose declared dependencies are satisfied.
- **Response integrator:** combines outputs and marks evidence vs. assumptions.
- **Shared portfolio:** appends a provenance record to a local JSONL file. Remote publishing is intentionally outside the default path.

## Provider and cost notes

The creative adapter is an interface seam, not a claim that a particular Gemini model identifier is currently available. Provider SDKs, model IDs, output formats, usage terms, and prices change; verify them against current vendor documentation before connecting a real service. The earlier `$0.03` per-image figure is not treated as verified pricing. API usage can incur charges.

## Quick start

Python 3.11+; no third-party dependencies for the local simulation:

```bash
python research/annaban_frontier_orchestrator.py
```

The script writes a sample record to `research/portfolio.jsonl`. Do not commit private prompts, API keys, personal data, or generated assets without reviewing their licensing and privacy implications.

## Validation checklist

- [ ] Unit tests cover routing, dependency ordering, and portfolio provenance.
- [ ] Provider integration is disabled until credentials and current model identifiers are verified.
- [ ] Human review precedes any external publishing or operational action.
- [ ] Outputs distinguish verified facts, assumptions, simulations, and unresolved questions.
- [ ] No cost, safety, performance, or environmental benefit is represented as measured without evidence.

## Attribution and evidence policy

Project-level authorship attribution is not a determination of legal ownership. Public examples are research artifacts and do not prove deployment, external commitments, revenue, or real-world outcomes. Maintain source links and version history for contributions; label simulations explicitly.
