"""
AnnabanAI — Enhanced Agent Hierarchy

Self-contained conceptual agent hierarchy for simulation and testing.
No network, filesystem, external-effect, or autonomous-authority behavior is
implemented here.

Hierarchy:
    EnhancedBaseAgent
      ├── EmpathAgent
      ├── TaskAgent
      └── SocialAgent
"""

from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class AgentState(str, Enum):
    IDLE = "idle"
    REFLECTING = "reflecting"
    WORKING = "working"
    SAFE_HOLD = "safe_hold"


@dataclass
class Memory:
    content: str
    source: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5
    emotional_valence: float = 0.0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: dt.datetime = field(default_factory=dt.datetime.now)
    last_accessed: dt.datetime = field(default_factory=dt.datetime.now)
    access_count: int = 0

    def __post_init__(self) -> None:
        self.importance = max(0.0, min(1.0, float(self.importance)))
        self.emotional_valence = max(-1.0, min(1.0, float(self.emotional_valence)))

    def access(self) -> None:
        self.last_accessed = dt.datetime.now()
        self.access_count += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "context": self.context,
            "importance": self.importance,
            "emotional_valence": self.emotional_valence,
            "timestamp": self.timestamp.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
        }


class MemorySystem:
    def __init__(self, capacity: int = 1000, short_term_limit: int = 50) -> None:
        if capacity < 1 or short_term_limit < 1:
            raise ValueError("capacity and short_term_limit must be positive")
        self.short_term_memory: List[Memory] = []
        self.long_term_memory: List[Memory] = []
        self.capacity = capacity
        self.short_term_limit = short_term_limit
        self.last_consolidation = dt.datetime.now()

    def add_memory(
        self,
        content: str,
        source: str = "",
        context: Optional[Dict[str, Any]] = None,
        importance: float = 0.5,
        emotional_valence: float = 0.0,
    ) -> Memory:
        memory = Memory(
            content=content,
            source=source,
            context=context or {},
            importance=importance,
            emotional_valence=emotional_valence,
        )
        self.short_term_memory.append(memory)
        if len(self.short_term_memory) >= self.short_term_limit:
            self.consolidate_memories()
        return memory

    def recall(self, query: str, limit: int = 5) -> List[Memory]:
        if limit < 1:
            return []
        terms = {term.lower() for term in query.split() if term.strip()}
        candidates = self.short_term_memory + self.long_term_memory
        scored = []
        for memory in candidates:
            haystack = f"{memory.content} {memory.source}".lower()
            score = sum(term in haystack for term in terms)
            if score:
                scored.append((score, memory.importance, memory))
        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        results = [item[2] for item in scored[:limit]]
        for memory in results:
            memory.access()
        return results

    def consolidate_memories(self) -> Dict[str, Any]:
        if not self.short_term_memory:
            return {"consolidated": 0, "forgotten": 0}

        consolidated = 0
        forgotten = 0
        for memory in self.short_term_memory:
            if memory.importance >= 0.3:
                self.long_term_memory.append(memory)
                consolidated += 1
            else:
                forgotten += 1

        self.short_term_memory = []
        self.long_term_memory.sort(
            key=lambda memory: (memory.importance, memory.last_accessed),
            reverse=True,
        )
        if len(self.long_term_memory) > self.capacity:
            forgotten += len(self.long_term_memory) - self.capacity
            self.long_term_memory = self.long_term_memory[: self.capacity]

        self.last_consolidation = dt.datetime.now()
        return {
            "consolidated": consolidated,
            "forgotten": forgotten,
            "timestamp": self.last_consolidation.isoformat(),
        }


@dataclass
class Intent:
    name: str
    confidence: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.confidence = max(0.0, min(1.0, float(self.confidence)))


@dataclass
class Task:
    name: str
    priority: int = 0
    status: str = "queued"
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Relationship:
    agent_id: str
    trust: float = 0.5
    interactions: int = 0

    def __post_init__(self) -> None:
        self.trust = max(0.0, min(1.0, float(self.trust)))


class EnhancedBaseAgent:
    """Base agent with bounded state, memory, intent tracking, and reflection."""

    def __init__(
        self,
        agent_id: str,
        name: Optional[str] = None,
        memory_capacity: int = 1000,
        persona: str = "shy_ambitious_developer",
    ) -> None:
        self.agent_id = agent_id
        self.name = name or agent_id
        self.persona = persona
        self.memory = MemorySystem(capacity=memory_capacity)
        self.intents: List[Intent] = []
        self.state = AgentState.IDLE
        self.reflections: List[str] = []
        self.capabilities: Set[str] = set()

    def remember(self, content: str, source: str = "", importance: float = 0.5, **context: Any) -> Memory:
        return self.memory.add_memory(
            content=content,
            source=source,
            importance=importance,
            context=context,
        )

    def track_intent(
        self, name: str, confidence: float = 0.0, **context: Any
    ) -> Intent:
        intent = Intent(name=name, confidence=confidence, context=context)
        self.intents.append(intent)
        return intent

    def reflect(self, observation: str) -> str:
        self.state = AgentState.REFLECTING
        reflection = f"{self.name}: {observation}"
        self.reflections.append(reflection)
        self.remember(reflection, source="reflection", importance=0.6)
        self.state = AgentState.IDLE
        return reflection

    def enter_safe_hold(self, reason: str) -> None:
        self.state = AgentState.SAFE_HOLD
        self.remember(f"SAFE_HOLD: {reason}", source="governance", importance=1.0)

    def resume(self) -> None:
        if self.state == AgentState.SAFE_HOLD:
            self.state = AgentState.IDLE

    def snapshot(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "persona": self.persona,
            "state": self.state.value,
            "capabilities": sorted(self.capabilities),
            "intent_count": len(self.intents),
            "reflection_count": len(self.reflections),
            "short_term_memory": len(self.memory.short_term_memory),
            "long_term_memory": len(self.memory.long_term_memory),
        }


class EmpathAgent(EnhancedBaseAgent):
    """Tracks emotional context without claiming access to a person's inner state."""

    def __init__(self, agent_id: str, name: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(agent_id, name, **kwargs)
        self.capabilities.update({"emotional_context", "intent_interpretation"})

    def assess_context(self, text: str) -> Dict[str, Any]:
        lowered = text.lower()
        cues = {
            "positive": any(word in lowered for word in ("excited", "happy", "hopeful")),
            "negative": any(word in lowered for word in ("worried", "sad", "frustrated")),
            "uncertain": any(word in lowered for word in ("maybe", "unsure", "uncertain")),
        }
        return {"text": text, "cues": cues, "inference_status": "contextual_only"}


class TaskAgent(EnhancedBaseAgent):
    """Maintains a local task queue and bounded resource model."""

    def __init__(self, agent_id: str, name: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(agent_id, name, **kwargs)
        self.capabilities.update({"task_management", "resource_tracking"})
        self.tasks: List[Task] = []
        self.resources = {"energy": 1.0, "focus": 1.0, "creativity": 1.0}

    def enqueue(self, name: str, priority: int = 0, **metadata: Any) -> Task:
        task = Task(name=name, priority=priority, metadata=metadata)
        self.tasks.append(task)
        self.tasks.sort(key=lambda item: item.priority, reverse=True)
        return task

    def next_task(self) -> Optional[Task]:
        for task in self.tasks:
            if task.status == "queued":
                return task
        return None

    def complete(self, task_id: str) -> bool:
        for task in self.tasks:
            if task.id == task_id and task.status == "queued":
                task.status = "completed"
                return True
        return False

    def set_resource(self, resource: str, value: float) -> None:
        if resource not in self.resources:
            raise KeyError(resource)
        self.resources[resource] = max(0.0, min(1.0, float(value)))


class SocialAgent(EnhancedBaseAgent):
    """Models collaboration state using explicit interaction records."""

    def __init__(self, agent_id: str, name: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(agent_id, name, **kwargs)
        self.capabilities.update({"relationship_tracking", "collaboration"})
        self.relationships: Dict[str, Relationship] = {}

    def interact(self, agent_id: str, trust_delta: float = 0.0) -> Relationship:
        relationship = self.relationships.setdefault(
            agent_id, Relationship(agent_id=agent_id)
        )
        relationship.trust = max(0.0, min(1.0, relationship.trust + trust_delta))
        relationship.interactions += 1
        return relationship

    def collaboration_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        relationship = self.relationships.get(agent_id)
        if relationship is None:
            return None
        return {
            "agent_id": relationship.agent_id,
            "trust": relationship.trust,
            "interactions": relationship.interactions,
        }


__all__ = [
    "AgentState",
    "Memory",
    "MemorySystem",
    "Intent",
    "Task",
    "Relationship",
    "EnhancedBaseAgent",
    "EmpathAgent",
    "TaskAgent",
    "SocialAgent",
]
