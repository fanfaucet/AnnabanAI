"""In-memory sessions; restart clears state and therefore fails closed."""
from __future__ import annotations
import secrets, time
from dataclasses import dataclass, field

@dataclass
class AgentSession:
    session_id: str
    agent_id: str
    provider: str
    status: str
    token_expires_at: int
    requested_capabilities: frozenset[str] = field(default_factory=frozenset)
    granted_capabilities: frozenset[str] = field(default_factory=frozenset)
    created_at: int = 0
    approved_by: str | None = None
    revoked_at: int | None = None

class SessionManager:
    def __init__(self, clock=time.time):
        self._clock = clock
        self._sessions: dict[str, AgentSession] = {}

    def create_pending(self, agent_id: str, provider: str, token_expires_at: int) -> AgentSession:
        session = AgentSession(secrets.token_urlsafe(32), agent_id, provider,
                               "pending_human_approval", token_expires_at,
                               created_at=int(self._clock()))
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> AgentSession:
        session = self._sessions.get(session_id)
        if session is None:
            raise PermissionError("Unknown session")
        if session.status not in {"revoked", "expired"} and int(self._clock()) >= session.token_expires_at:
            session.status, session.granted_capabilities = "expired", frozenset()
        return session

    def list_sessions(self) -> list[AgentSession]:
        for sid in list(self._sessions):
            self.get(sid)
        return list(self._sessions.values())

    def set_requested_capabilities(self, session_id: str, capabilities: frozenset[str]) -> AgentSession:
        session = self.get(session_id)
        if session.status != "pending_human_approval":
            raise PermissionError("Only pending sessions can request capabilities")
        session.requested_capabilities = capabilities
        return session

    def approve(self, session_id: str, approver_id: str, capabilities: frozenset[str]) -> AgentSession:
        if not approver_id.strip():
            raise PermissionError("Human approver identity is required")
        session = self.get(session_id)
        if session.status != "pending_human_approval":
            raise PermissionError("Only pending sessions can be approved")
        if not capabilities or not capabilities.issubset(session.requested_capabilities):
            raise PermissionError("Grant must be a non-empty subset of requested capabilities")
        session.status, session.approved_by = "active", approver_id
        session.granted_capabilities = capabilities
        return session

    def revoke(self, session_id: str, approver_id: str) -> AgentSession:
        if not approver_id.strip():
            raise PermissionError("Human operator identity is required")
        session = self.get(session_id)
        session.status, session.granted_capabilities = "revoked", frozenset()
        session.revoked_at = int(self._clock())
        return session
