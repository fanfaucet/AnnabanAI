# Agents

Agents perform actions, interact, and participate in collectives. `main.py` imports:
- `BaseAgent`, `Memory`, `Goal`
- `TaskAgent`, `SocialAgent`
- `AgentCollective`, `AgentRole`, `CollectiveTask`

> Note: This repository view only shows usage sites in `main.py`. For complete APIs, open the corresponding modules under `agents/`.

## Core Agent Concepts
- **BaseAgent**: base class for agents with identity, tokens, skills, messaging
- **Memory**: agent memory subsystem
- **Goal**: representation of agent goals

## Agent Types
- **TaskAgent(name: str)**: specializes in tasks and analysis
- **SocialAgent(name: str)**: specializes in communication and negotiation
- **ConversationalUserAgent(name: str)**: see [AnnabanAI](./annabanai.md)
- **LightningAgent(name: str)**: specializes in rapid response, triage, and time-sensitive execution

### Common Methods (as used in `main.py`)
- `earn_tokens(amount: float, reason: str) -> None`
- `learn_skill(name: str, level: float) -> None`
- `add_goal(description: str, priority: float) -> None`

## Collectives
- **AgentCollective(name: str)**: group of agents with roles and tasks
- Methods used in `main.py`:
  - `add_agent(agent: BaseAgent, role_name: str) -> None`
  - `create_task(description: str, difficulty: float, reward: float, required_roles: List[str]) -> CollectiveTask`
  - `assign_task_roles(task_id: str) -> None`
  - `execute_task(task_id: str) -> Dict[str, Any]`

## Messaging
- Agents can send messages via the `Environment`: `env.send_message(sender_id, recipient_id, message)`
