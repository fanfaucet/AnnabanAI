from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable


@dataclass(slots=True)
class ModuleContext:
    """Restricted context exposed to user modules."""

    user_id: str
    config: dict[str, Any]
    emit_event: Callable[[str, dict[str, Any]], None]
    logger: Callable[[str, str], None]
    storage_path: str


@dataclass(slots=True)
class ModuleResult:
    """Normalized response returned from module hooks."""

    status: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ModuleBase(ABC):
    """Base contract for all user-extensible AnnabanOS-Lite modules."""

    module_id: str = "base"
    version: str = "0.1.0"
    description: str = "Base module"
    permissions: tuple[str, ...] = ()
    default_state: dict[str, Any] = {}

    def __init__(self) -> None:
        self.state: dict[str, Any] = dict(self.default_state)

    @abstractmethod
    def on_load(self, context: ModuleContext) -> ModuleResult:
        raise NotImplementedError

    def on_tick(self, context: ModuleContext) -> ModuleResult:
        return ModuleResult(status="idle", message=f"{self.module_id} tick skipped")

    def on_event(self, event_type: str, payload: dict[str, Any], context: ModuleContext) -> ModuleResult:
        return ModuleResult(
            status="ignored",
            message=f"{self.module_id} ignored event {event_type}",
            data={"event_type": event_type},
        )

    def snapshot_state(self) -> dict[str, Any]:
        return dict(self.state)

    def restore_state(self, state: dict[str, Any] | None) -> None:
        self.state = dict(self.default_state)
        if state:
            self.state.update(state)
