# Environment & Virtual World

`Environment` coordinates agents, collectives, and messaging. `VirtualWorld` provides spatial simulation with locations, objects, and agent positions.

> Check the modules in `environment/` for complete interfaces.

## Environment
Likely responsibilities (as used in `main.py`):
- `register_agent(agent: BaseAgent) -> None`
- `register_collective(collective: AgentCollective) -> None`
- `send_message(sender_id: str, recipient_id: str, text: str) -> None`
- `agents: Dict[str, BaseAgent]`
- `collectives: Dict[str, AgentCollective]`

## VirtualWorld
Constructed as `VirtualWorld(name: str, size: Tuple[float, float])`.

Used methods in `main.py`:
- `add_agent(agent_id: str, position: Tuple[float, float], props: Dict[str, Any]) -> None`
- `move_agent(agent_id: str, new_position: Tuple[float, float]) -> None`
- `add_location(location: VirtualLocation) -> None`
- `add_object(obj: VirtualObject) -> None`
- `get_random_position() -> Tuple[float, float]`
- `get_agent_location(agent_id: str) -> Optional[VirtualLocation]`
- `get_agents_near(position: Tuple[float, float], radius: float) -> List[str]`

Related types:
- `VirtualLocation(name: str, center: Tuple[float, float], radius: float, props: Dict[str, Any])`
- `VirtualObject(name: str, position: Tuple[float, float], props: Dict[str, Any])`
