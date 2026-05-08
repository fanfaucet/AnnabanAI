from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Protocol

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SandboxedModule(Protocol):
    """Protocol for sandboxed AnnabanOS-Lite modules."""

    name: str

    def run(self, shared_state: Dict[str, Any]) -> Dict[str, Any]:
        ...


@dataclass
class ModuleExecutionRecord:
    module_name: str
    timestamp: str
    status: str
    alerts: List[str] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)


class AnnabanOSLiteKernel:
    """Minimal modular kernel with shared state and sandboxed module execution."""

    def __init__(self) -> None:
        self.shared_state: Dict[str, Any] = {
            "jacob_node": {
                "identity": {
                    "node_type": "personal_architect_node",
                    "public_lattice_isolation": True,
                    "ftdt_principal_usd": 6_692_000_000_000.0,
                    "ftdt_principal_touched": False,
                },
                "funding": {},
                "liquidity": {},
                "signals": {},
                "milestones": [],
                "alerts": [],
                "logs": [],
            }
        }
        self.execution_log: List[ModuleExecutionRecord] = []

    def register_state(self, key: str, value: Dict[str, Any]) -> None:
        self.shared_state.setdefault(key, value)

    def execute_module(self, module: SandboxedModule) -> Dict[str, Any]:
        sandbox_view = copy.deepcopy(self.shared_state)
        result = module.run(sandbox_view)

        allowed_keys = {"jacob_node"}
        for key in allowed_keys:
            if key in sandbox_view:
                self.shared_state[key] = sandbox_view[key]

        record = ModuleExecutionRecord(
            module_name=module.name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=result.get("status", "ok"),
            alerts=result.get("alerts", []),
            events=result.get("events", []),
        )
        self.execution_log.append(record)
        logger.info("Executed module %s with status %s", module.name, record.status)
        return result
