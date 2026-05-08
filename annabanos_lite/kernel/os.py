from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from annabanos_lite.kernel.config_manager import ConfigManager
from annabanos_lite.kernel.module_manager import ModuleExecutionRecord, ModuleManager
from annabanos_lite.kernel.persistence import PersistentStore
from annabanos_lite.kernel.services import FileService, SystemMonitor, TaskScheduler
from annabanos_lite.modules.ai_suggestions import AISuggestionModule
from annabanos_lite.modules.notifications import NotificationModule


class AnnabanOSLite:
    """Composable operating environment that keeps kernel services separate from user modules."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[1]
        self.data_root = self.root / "data"
        self.config_root = self.root / "config"
        self.store = PersistentStore(self.data_root)
        self.config_manager = ConfigManager(self.config_root)
        self.file_service = FileService(self.data_root / "files")
        self.scheduler = TaskScheduler()
        self.monitor = SystemMonitor()
        self.logs: list[dict[str, Any]] = []
        self.module_manager = ModuleManager(self.data_root, self.log)
        self._register_builtin_modules()

    def _register_builtin_modules(self) -> None:
        self.module_manager.register(NotificationModule())
        self.module_manager.register(AISuggestionModule())

    def log(self, level: str, message: str) -> None:
        entry = {"level": level, "message": message, "timestamp": datetime.utcnow().isoformat()}
        self.logs.append(entry)
        self.store.append_log("logs/system_logs.json", entry)

    def boot(self, user_id: str = "default") -> dict[str, Any]:
        config = self.config_manager.load_user_config(user_id)
        module_records = self.module_manager.load_enabled_modules(user_id, config)
        self.log("info", f"Boot completed for user {user_id}")
        return {
            "user_id": user_id,
            "config": config,
            "modules": [asdict(record) for record in module_records],
            "system": self.monitor.snapshot(list(self.module_manager.registry.keys()), len(self.scheduler.tasks)),
        }

    def run_cycle(self, user_id: str = "default") -> dict[str, Any]:
        config = self.config_manager.load_user_config(user_id)
        tick_records = self.module_manager.tick(user_id, config)
        snapshot = self.monitor.snapshot(config.get("enabled_modules", []), len(self.scheduler.tasks))
        self.store.write_json("state/last_snapshot.json", snapshot)
        return {
            "ticks": [asdict(record) for record in tick_records],
            "system": snapshot,
            "events": list(self.module_manager.event_log),
        }

    def trigger_event(self, event_type: str, payload: dict[str, Any], user_id: str = "default") -> list[ModuleExecutionRecord]:
        config = self.config_manager.load_user_config(user_id)
        records = self.module_manager.dispatch_event(user_id, config, event_type, payload)
        self.store.append_log(
            "logs/events.json",
            {"event_type": event_type, "payload": payload, "user_id": user_id, "timestamp": datetime.utcnow().isoformat()},
        )
        return records
