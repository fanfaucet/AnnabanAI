"""Explicit allow-list for external-agent capabilities."""
from dataclasses import dataclass

FORBIDDEN_CAPABILITIES = frozenset({
    "kernel_boot", "policy_edit", "audit_edit", "scheduler_access",
    "spawn_agent", "external_execution", "credential_read",
})

@dataclass(frozen=True)
class CapabilityPolicy:
    capabilities_by_agent: dict[str, frozenset[str]]

    def allowed_for(self, agent_id: str) -> frozenset[str]:
        return self.capabilities_by_agent.get(agent_id, frozenset())

    def validate_request(self, agent_id: str, requested: set[str]) -> frozenset[str]:
        if not requested:
            raise PermissionError("At least one capability must be requested")
        if requested & FORBIDDEN_CAPABILITIES:
            raise PermissionError("Request includes a forbidden capability")
        unknown = requested - self.allowed_for(agent_id)
        if unknown:
            raise PermissionError("Capabilities not allow-listed: " + ", ".join(sorted(unknown)))
        return frozenset(requested)
