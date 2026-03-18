from __future__ import annotations

from annabanos_lite.kernel.base import ModuleBase, ModuleContext, ModuleResult


class NotificationModule(ModuleBase):
    module_id = "notifications"
    version = "1.0.0"
    description = "User notification center with persistent reminders"
    permissions = ("emit_event", "write_module_state")
    default_state = {"notifications": []}

    def on_load(self, context: ModuleContext) -> ModuleResult:
        context.logger("info", "Notification module ready")
        return ModuleResult(status="loaded", message="Notification center initialized")

    def on_tick(self, context: ModuleContext) -> ModuleResult:
        count = len(self.state["notifications"])
        return ModuleResult(status="ready", message=f"{count} notifications available")

    def on_event(self, event_type: str, payload: dict[str, object], context: ModuleContext) -> ModuleResult:
        if event_type != "notify":
            return super().on_event(event_type, payload, context)
        message = str(payload.get("message", "No message provided"))
        self.state["notifications"].append({"message": message, "level": payload.get("level", "info")})
        context.emit_event("notification_stored", {"count": len(self.state["notifications"])})
        return ModuleResult(status="stored", message=f"Stored notification: {message}")
