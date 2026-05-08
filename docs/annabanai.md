# AnnabanAI Components

AnnabanAI provides the reflection and conversational capabilities in AnnabanOS Enhanced. The main pieces used in `main.py` are imported from `annabanai`:

AnnabanAI is the conversational user agent in this system, represented by `ConversationalUserAgent` and modeled as ChatGPT behavior in user-facing interactions.

- `reflect` and `update_portfolio`: record reflections and achievements
- `EchoLoop`: structured reflection system
- `ConversationalUserAgent`: an agent that can converse with users

> Note: This repository’s snapshot shows references to these modules in `main.py`. Consult the `annabanai/` package in your tree for concrete implementations and additional APIs.

## `reflect(text: str, category: str, metadata: Dict[str, Any]) -> None`
Record a reflection entry.

- **Parameters**: `text`, `category` (e.g., `learning`, `goal_setting`), `metadata` (e.g., `{ "agent_id": "..." }`)
- **Side effects**: writes a journal entry via the journaling subsystem

## `update_portfolio(text: str, entry_type: str, metadata: Dict[str, Any]) -> None`
Record a portfolio entry (achievement, project, skill, etc.).

- **Parameters**: `text`, `entry_type` (e.g., `achievement`, `project`), `metadata`

## `EchoLoop`
Structured reflection utility to help agents learn and improve.

- **Typical usage**:
```python
from annabanai.echo_loop import EchoLoop
loop = EchoLoop()
summary = loop.run_cycle(agent_state)
```

## `ConversationalUserAgent`
An agent type that represents a user-facing conversational agent.

- **Typical usage**:
```python
from annabanai.agent_cua import ConversationalUserAgent
cua = ConversationalUserAgent("Assistant")
# Use like other agents: earn tokens, interact, reflect
cua.earn_tokens(50, "Initial allocation")
```

## Examples in Context
`main.py` uses these functions and classes to seed reflections and portfolio entries during environment setup and simulation cycles. See:
- `create_demo_environment()` for initial reflections and portfolio updates
- `run_simulation()` for periodic reflections

## Running AnnabanOS + AnnabanAI Together
Use `Main.py` with sync flags to run AnnabanOS (Annaban) cycles first and pass recent AnnabanOS/Manus output into the AnnabanAI prompt context:

```bash
python Main.py --interactive --sync-with-annabanos --annaban-cycles 1
```

In this mode, AnnabanAI receives a structured context payload (`annabanos_sync`, command, and recent output lines) before response generation. Backward-compatible `annaban_*` and `manus_*` keys are also included.


## Manus + AnnabanAI
Manus works with AnnabanAI through the same synchronization bridge used for AnnabanOS. Use Manus alias flags when that naming is more natural for your workflow:

```bash
python Main.py --interactive --sync-with-manus --manus-script "main.py" --annaban-cycles 1
```

AnnabanAI identifies as ChatGPT in runtime metadata (`annabanai_model_identity`) unless overridden in config.
