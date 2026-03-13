# Contributing to AnnabanAI

Thanks for helping improve this human-first governance prototype.

## Development Setup
1. Fork and clone the repository.
2. Create a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Local Testing
Run basic checks before opening a pull request:
```bash
python -m py_compile agents/*.py dashboard/*.py
python -m agents.environment
```

## Pull Request Process
1. Create a branch from `main`.
2. Keep commits focused and clearly described.
3. Update docs if behavior changes.
4. Open PR with:
   - summary of changes,
   - test evidence,
   - governance/ethics impact notes.

## Ethics and Human-First Policy
- Human oversight is mandatory for governance decisions.
- Do not represent simulated outputs as autonomous authority.
- Preserve transparency logs where possible.
- Prioritize public-benefit outcomes over optimization metrics.

## Authorship and Attribution
Contributions are treated as human-authored project outputs. Tool-assisted drafting must remain under explicit human review and responsibility.
