# Lattice Metrics Harness

The Grok Harness is a local demonstration runner for AnnabanAI's Lattice Metrics module.

## Run

From the repository root:

```bash
python -m unittest discover -s tests -v
python examples/grok_harness.py
python examples/grok_harness.py --cycles 5 --seed 7
python examples/grok_harness.py --no-real-agents
python examples/grok_harness.py --no-samples --no-real-agents --random-seed
```

Use `--history PATH` to choose where the JSON history file is written.

## Provenance boundary

- With the sample registry enabled, agent counts describe only the in-memory registry created by this process. They are not discovered live agents.
- With `--no-real-agents`, agent counts are generated synthetically.
- Expansion, joy density, sovereignty, and stability remain synthetic demonstration values in both modes.
- No external runtime, governance environment, or production telemetry is connected.
