# API Reference

This reference documents public functions exposed in `main.py` and the core components they orchestrate. See dedicated pages for component-specific APIs.

- Agents: see [Agents](./agents.md)
- Environment & World: see [Environment](./environment.md)
- Token Economy: see [Token Economy](./token_economy.md)
- Wallets: see [Blockchain Wallet Capabilities](./wallet_capabilities.md)
- AnnabanAI: see [AnnabanAI Components](./annabanai.md)

## `load_task_scenarios(file_path: str) -> List[Dict[str, Any]]`
Load task scenarios from a JSON file.

- **Parameters**: `file_path` – path to JSON
- **Returns**: list of scenario dicts (empty on error)
- **Example**:
```python
from main import load_task_scenarios
scenarios = load_task_scenarios("tasks/task_scenarios.json")
```

## `create_demo_environment() -> Environment`
Create an environment pre-populated with example agents (task, social, conversational) and a collective with roles.

- **Returns**: `Environment`
- **Side effects**: agents are given initial tokens, skills, and goals; reflections and portfolio entries are recorded
- **Example**:
```python
from main import create_demo_environment
env = create_demo_environment()
print(list(env.agents.keys()))
```

## `create_virtual_world(env: Environment) -> VirtualWorld`
Create a virtual world, register agents with positions/icons, and seed locations/objects.

- **Parameters**: `env` – environment returned by `create_demo_environment`
- **Returns**: `VirtualWorld`
- **Example**:
```python
from main import create_demo_environment, create_virtual_world
env = create_demo_environment()
world = create_virtual_world(env)
```

## `setup_token_economy() -> Tuple[TokenManager, TokenMarketplace]`
Initialize token manager and marketplace.

- **Returns**: `(token_manager, marketplace)`
- **Example**:
```python
from main import setup_token_economy
manager, market = setup_token_economy()
```

## `create_marketplace_listings(marketplace: TokenMarketplace, env: Environment) -> None`
Create initial example listings for available agents.

- **Parameters**: `marketplace`, `env`
- **Example**:
```python
from main import create_demo_environment, setup_token_economy, create_marketplace_listings
env = create_demo_environment()
manager, market = setup_token_economy()
create_marketplace_listings(market, env)
```

## `run_simulation(env: Environment, world: VirtualWorld, token_manager: TokenManager, marketplace: TokenMarketplace, num_cycles: int = 5) -> None`
Run a simulation loop over `num_cycles`, moving agents, sending messages, executing collective tasks, transacting in the marketplace, applying interest, and recording reflections.

- **Parameters**: `env`, `world`, `token_manager`, `marketplace`, `num_cycles`
- **Example**: see [Usage](./usage.md)

## `main()`
CLI entry point. Parses args (`--config`, `--cycles`, `--scenarios`), wires components, and runs the simulation.

- **Run**:
```bash
python main.py --cycles 5
```

## Notes
- Type annotations in `main.py` rely on classes imported from subpackages (e.g., `Environment`, `VirtualWorld`). See component pages for details.
- In some environments, you may need `from __future__ import annotations` or ensure all types are imported where used in annotations.
