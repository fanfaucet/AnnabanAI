from __future__ import annotations

from pathlib import Path

from annabanos_lite.kernel.base import ModuleBase, ModuleContext, ModuleResult
from annabanos_lite.kernel.os import AnnabanOSLite


class CrashingModule(ModuleBase):
    module_id = "crashing"

    def on_load(self, context: ModuleContext) -> ModuleResult:
        raise RuntimeError("boom")


def test_boot_loads_builtin_modules(tmp_path: Path) -> None:
    os_app = AnnabanOSLite(root=tmp_path)
    result = os_app.boot("alice")

    assert result["user_id"] == "alice"
    assert {module["module_id"] for module in result["modules"]} == {"notifications", "ai_suggestions"}
    assert result["system"]["status"] == "healthy"


def test_notification_event_persists_state(tmp_path: Path) -> None:
    os_app = AnnabanOSLite(root=tmp_path)
    os_app.boot("alice")
    records = os_app.trigger_event("notify", {"message": "Check focus mode"}, user_id="alice")

    assert any(record.status == "stored" for record in records)
    module_state = os_app.store.read_json("module_state/alice/notifications.json", default={})
    assert module_state["notifications"][0]["message"] == "Check focus mode"


def test_sandbox_contains_module_failures(tmp_path: Path) -> None:
    os_app = AnnabanOSLite(root=tmp_path)
    os_app.module_manager.register(CrashingModule())
    config = os_app.config_manager.load_user_config("default")
    config["enabled_modules"].append("crashing")
    os_app.config_manager.save_user_config("default", config)

    result = os_app.boot("default")
    crashing = next(module for module in result["modules"] if module["module_id"] == "crashing")
    assert crashing["status"] == "sandboxed"


def test_run_cycle_generates_ai_suggestion(tmp_path: Path) -> None:
    os_app = AnnabanOSLite(root=tmp_path)
    os_app.boot("alice")
    result = os_app.run_cycle("alice")

    generated = next(record for record in result["ticks"] if record["module_id"] == "ai_suggestions")
    assert generated["status"] == "generated"
    snapshot = os_app.store.read_json("state/last_snapshot.json", default={})
    assert snapshot["status"] == "healthy"
