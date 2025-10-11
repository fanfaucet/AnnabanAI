# Usage

## CLI
Run a simulation for a given number of cycles:
```bash
python main.py --cycles 5
```

Optional flags:
- `--config <path>`: path to configuration YAML file (loads before run)
- `--scenarios <path>`: path to task scenarios JSON file

Examples:
```bash
python main.py --cycles 10 --config config/config.yaml
python main.py --scenarios tasks/task_scenarios.json
```

## Programmatic Usage
You can construct the system and run a simulation from Python:
```python
from main import (
    create_demo_environment,
    create_virtual_world,
    setup_token_economy,
    create_marketplace_listings,
    run_simulation,
)

# 1) Environment with agents/collectives
env = create_demo_environment()

# 2) Virtual world
world = create_virtual_world(env)

# 3) Token economy + marketplace
token_manager, marketplace = setup_token_economy()
create_marketplace_listings(marketplace, env)

# 4) Run
run_simulation(env, world, token_manager, marketplace, num_cycles=5)
```

## Configuration & Scenarios
- Config: `config/config.yaml` (see comments in file for options)
- Scenarios JSON: used by `load_task_scenarios()` to seed tasks
