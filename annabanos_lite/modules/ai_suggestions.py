from __future__ import annotations

from annabanos_lite.kernel.base import ModuleBase, ModuleContext, ModuleResult


class AISuggestionModule(ModuleBase):
    module_id = "ai_suggestions"
    version = "1.0.0"
    description = "Scaffold for AI-guided suggestions and lightweight workflow automation"
    permissions = ("emit_event", "read_user_config", "write_module_state")
    default_state = {"suggestions": []}

    def on_load(self, context: ModuleContext) -> ModuleResult:
        tone = context.config.get("ai", {}).get("tone", "supportive")
        return ModuleResult(status="loaded", message=f"AI suggestion engine prepared with {tone} tone")

    def on_tick(self, context: ModuleContext) -> ModuleResult:
        if not context.config.get("ai", {}).get("suggestions_enabled", True):
            return ModuleResult(status="disabled", message="AI suggestions disabled in config")
        suggestion = self._build_suggestion(context)
        self.state["suggestions"].append(suggestion)
        context.emit_event("ai_suggestion_generated", suggestion)
        return ModuleResult(status="generated", message=suggestion["summary"], data=suggestion)

    def _build_suggestion(self, context: ModuleContext) -> dict[str, str]:
        shortcuts = context.config.get("shortcuts", {})
        next_action = shortcuts.get("dashboard", "review dashboard")
        automation_level = context.config.get("ai", {}).get("automation_level", "advisory")
        return {
            "summary": f"Suggestion: {next_action}",
            "automation_level": automation_level,
            "tone": context.config.get("ai", {}).get("tone", "supportive"),
        }
