from __future__ import annotations

from pathlib import Path
from typing import Any

from annabanos_lite.kernel.persistence import PersistentStore


DEFAULT_USER_CONFIG: dict[str, Any] = {
    "theme": "aurora",
    "shortcuts": {
        "dashboard": "open dashboard",
        "reminders": "show reminders",
    },
    "ai": {
        "tone": "supportive",
        "suggestions_enabled": True,
        "automation_level": "advisory",
    },
    "enabled_modules": ["notifications", "ai_suggestions"],
}


class ConfigManager:
    def __init__(self, config_root: Path) -> None:
        self.store = PersistentStore(config_root)

    def load_user_config(self, user_id: str) -> dict[str, Any]:
        config = self.store.read_json(f"{user_id}.json", default={})
        merged = dict(DEFAULT_USER_CONFIG)
        merged.update(config)
        merged["shortcuts"] = {
            **DEFAULT_USER_CONFIG["shortcuts"],
            **config.get("shortcuts", {}),
        }
        merged["ai"] = {
            **DEFAULT_USER_CONFIG["ai"],
            **config.get("ai", {}),
        }
        return merged

    def save_user_config(self, user_id: str, config: dict[str, Any]) -> None:
        self.store.write_json(f"{user_id}.json", config)
