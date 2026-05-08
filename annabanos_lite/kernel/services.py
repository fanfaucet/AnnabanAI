from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class FileService:
    root: Path

    def save_text(self, relative_path: str, content: str) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def read_text(self, relative_path: str) -> str:
        return (self.root / relative_path).read_text()


@dataclass(slots=True)
class TaskScheduler:
    tasks: list[dict[str, Any]] = field(default_factory=list)

    def schedule(self, name: str, command: str, priority: str = "normal") -> dict[str, Any]:
        task = {
            "name": name,
            "command": command,
            "priority": priority,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.tasks.append(task)
        return task

    def list_tasks(self) -> list[dict[str, Any]]:
        return list(self.tasks)


@dataclass(slots=True)
class SystemMonitor:
    def snapshot(self, active_modules: list[str], scheduled_tasks: int) -> dict[str, Any]:
        return {
            "status": "healthy",
            "active_modules": active_modules,
            "scheduled_tasks": scheduled_tasks,
            "timestamp": datetime.utcnow().isoformat(),
        }
