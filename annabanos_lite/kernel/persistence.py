from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PersistentStore:
    """Simple JSON-backed persistence helper for settings, logs, and module state."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def read_json(self, relative_path: str, default: Any) -> Any:
        path = self.root / relative_path
        if not path.exists():
            return default
        return json.loads(path.read_text())

    def write_json(self, relative_path: str, payload: Any) -> None:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True))

    def append_log(self, relative_path: str, entry: dict[str, Any]) -> None:
        current = self.read_json(relative_path, default=[])
        current.append(entry)
        self.write_json(relative_path, current)
