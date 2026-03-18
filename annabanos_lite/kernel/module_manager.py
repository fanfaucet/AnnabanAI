from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from annabanos_lite.kernel.base import ModuleBase, ModuleContext, ModuleResult
from annabanos_lite.kernel.persistence import PersistentStore


@dataclass(slots=True)
class ModuleExecutionRecord:
    module_id: str
    hook: str
    status: str
    message: str


class ModuleSandboxError(RuntimeError):
    pass


class ModuleManager:
    """Registers and executes user modules behind a narrow sandbox contract."""

    def __init__(self, data_root: Path, logger) -> None:
        self.registry: dict[str, ModuleBase] = {}
        self.store = PersistentStore(data_root / "module_state")
        self.logger = logger
        self.event_log: list[dict[str, Any]] = []

    def register(self, module: ModuleBase) -> None:
        if module.module_id in self.registry:
            raise ValueError(f"Module {module.module_id} already registered")
        self.registry[module.module_id] = module

    def load_enabled_modules(self, user_id: str, config: dict[str, Any]) -> list[ModuleExecutionRecord]:
        records: list[ModuleExecutionRecord] = []
        for module_id in config.get("enabled_modules", []):
            module = self.registry.get(module_id)
            if not module:
                records.append(ModuleExecutionRecord(module_id, "on_load", "missing", "Module not found"))
                continue
            module.restore_state(self.store.read_json(f"{user_id}/{module_id}.json", default={}))
            result = self._execute(module, "on_load", user_id, config)
            records.append(ModuleExecutionRecord(module_id, "on_load", result.status, result.message))
        return records

    def tick(self, user_id: str, config: dict[str, Any]) -> list[ModuleExecutionRecord]:
        return [
            ModuleExecutionRecord(module_id, "on_tick", result.status, result.message)
            for module_id, result in self._run_hook("on_tick", user_id, config)
        ]

    def dispatch_event(self, user_id: str, config: dict[str, Any], event_type: str, payload: dict[str, Any]) -> list[ModuleExecutionRecord]:
        records: list[ModuleExecutionRecord] = []
        for module_id in config.get("enabled_modules", []):
            module = self.registry.get(module_id)
            if not module:
                continue
            context = self._build_context(module_id, user_id, config)
            try:
                result = module.on_event(event_type, payload, context)
                self._persist_state(user_id, module)
                records.append(ModuleExecutionRecord(module_id, "on_event", result.status, result.message))
            except Exception as exc:
                self.logger("error", f"Sandbox isolated module {module_id}: {exc}")
                records.append(ModuleExecutionRecord(module_id, "on_event", "sandboxed", str(exc)))
        return records

    def _run_hook(self, hook: str, user_id: str, config: dict[str, Any]):
        for module_id in config.get("enabled_modules", []):
            module = self.registry.get(module_id)
            if not module:
                continue
            yield module_id, self._execute(module, hook, user_id, config)

    def _execute(self, module: ModuleBase, hook: str, user_id: str, config: dict[str, Any]) -> ModuleResult:
        context = self._build_context(module.module_id, user_id, config)
        try:
            result = getattr(module, hook)(context)
            self._persist_state(user_id, module)
            return result
        except Exception as exc:
            self.logger("error", f"Sandbox isolated module {module.module_id}: {exc}")
            return ModuleResult(status="sandboxed", message=str(exc), data={"module": module.module_id})

    def _build_context(self, module_id: str, user_id: str, config: dict[str, Any]) -> ModuleContext:
        storage_path = str((self.store.root / user_id / module_id).resolve())
        Path(storage_path).mkdir(parents=True, exist_ok=True)
        return ModuleContext(
            user_id=user_id,
            config=config,
            emit_event=lambda event_type, payload: self.event_log.append(
                {"module_id": module_id, "event_type": event_type, "payload": payload}
            ),
            logger=lambda level, message: self.logger(level, f"[{module_id}] {message}"),
            storage_path=storage_path,
        )

    def _persist_state(self, user_id: str, module: ModuleBase) -> None:
        self.store.write_json(f"{user_id}/{module.module_id}.json", module.snapshot_state())
