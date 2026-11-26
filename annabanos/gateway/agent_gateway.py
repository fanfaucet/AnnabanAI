"""Human-gated external-agent gateway. No provider calls or code execution."""
from __future__ import annotations
import hashlib, hmac, json, os, threading, time
from pathlib import Path
from typing import Any
from .auth_manager import AuthManager
from .capability_policy import CapabilityPolicy, FORBIDDEN_CAPABILITIES
from .session_manager import AgentSession, SessionManager

class JsonlAuditLedger:
    """Hash-chained JSONL audit ledger. Tamper-evident, not tamper-proof."""
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else None
        self._lock = threading.Lock()
        self._previous_hash = "0" * 64
        self.records: list[dict[str, Any]] = []
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.path.exists() and self.path.stat().st_size:
                raise RuntimeError("Existing ledger requires chain verification before append")

    def append(self, event: str, **fields: Any) -> dict[str, Any]:
        with self._lock:
            body = {"timestamp": int(time.time()), "event": event, **fields,
                    "previous_hash": self._previous_hash}
            canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
            digest = hashlib.sha256(canonical.encode()).hexdigest()
            record = {**body, "record_hash": digest}
            line = json.dumps(record, sort_keys=True, separators=(",", ":")) + "\\n"
            if self.path:
                fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
                try:
                    os.write(fd, line.encode())
                    os.fsync(fd)
                finally:
                    os.close(fd)
            self.records.append(record)
            self._previous_hash = digest
            return record

class AgentGateway:
    def __init__(self, auth: AuthManager, policy: CapabilityPolicy,
                 sessions: SessionManager | None = None, audit: JsonlAuditLedger | None = None,
                 human_approval_key: str | None = None):
        self.auth, self.policy = auth, policy
        self.sessions = sessions or SessionManager()
        self.audit = audit or JsonlAuditLedger()
        # The key is a separate control-plane credential; an approver name alone is not authentication.
        self._human_approval_key_digest = (
            hashlib.sha256(human_approval_key.encode()).hexdigest()
            if human_approval_key else None
        )

    def _verify_human(self, approval_key: str | None) -> None:
        if self._human_approval_key_digest is None or not approval_key:
            raise PermissionError("Human approval authentication is not configured")
        supplied = hashlib.sha256(approval_key.encode()).hexdigest()
        if not hmac.compare_digest(self._human_approval_key_digest, supplied):
            raise PermissionError("Invalid human approval credential")

    def login(self, agent_id: str, api_key: str, signed_token: str,
              requested_capabilities: set[str]) -> dict[str, Any]:
        try:
            verified = self.auth.verify(agent_id, api_key, signed_token)
            identity = self.auth.identity(agent_id)
            requested = self.policy.validate_request(agent_id, requested_capabilities)
            if not requested.issubset(identity.allowed_capabilities):
                raise PermissionError("Capability exceeds registered identity ceiling")
            session = self.sessions.create_pending(agent_id, verified.provider, verified.expires_at)
            self.sessions.set_requested_capabilities(session.session_id, requested)
            self.audit.append("EXTERNAL_AGENT_LOGIN_VERIFIED", agent_id=agent_id,
                              session_id=session.session_id, status=session.status,
                              requested_capabilities=sorted(requested),
                              token_nonce_hash=hashlib.sha256(verified.nonce.encode()).hexdigest(),
                              external_effects=0)
            return {"status": "awaiting_human_approval", "session_id": session.session_id,
                    "requested_capabilities": sorted(requested), "external_effects": 0}
        except (PermissionError, ValueError) as exc:
            self.audit.append("EXTERNAL_AGENT_LOGIN_DENIED", agent_id=agent_id,
                              reason=str(exc), external_effects=0)
            return {"status": "denied", "reason": str(exc), "external_effects": 0}

    def approve(self, session_id: str, approver_id: str, capabilities: set[str],
                approval_key: str | None = None) -> dict[str, Any]:
        try:
            self._verify_human(approval_key)
            agent_id = self.sessions.get(session_id).agent_id
            approved = self.policy.validate_request(agent_id, capabilities)
            session = self.sessions.approve(session_id, approver_id, approved)
            self.audit.append("EXTERNAL_AGENT_SESSION_GRANTED", agent_id=agent_id,
                              session_id=session_id, approver_id=approver_id,
                              capabilities=sorted(approved), external_effects=0)
            return self._view(session)
        except (PermissionError, ValueError) as exc:
            self.audit.append("EXTERNAL_AGENT_APPROVAL_DENIED", session_id=session_id,
                              approver_id=approver_id, reason=str(exc), external_effects=0)
            return {"status": "denied", "reason": str(exc), "external_effects": 0}

    def list_sessions(self) -> list[dict[str, Any]]:
        return [self._view(s) for s in self.sessions.list_sessions()]

    def revoke(self, session_id: str, approver_id: str,
               approval_key: str | None = None) -> dict[str, Any]:
        try:
            self._verify_human(approval_key)
            session = self.sessions.revoke(session_id, approver_id)
            self.audit.append("EXTERNAL_AGENT_SESSION_REVOKED", agent_id=session.agent_id,
                              session_id=session_id, approver_id=approver_id, external_effects=0)
            return self._view(session)
        except PermissionError as exc:
            self.audit.append("EXTERNAL_AGENT_REVOCATION_DENIED", session_id=session_id,
                              approver_id=approver_id, reason=str(exc), external_effects=0)
            return {"status": "denied", "reason": str(exc), "external_effects": 0}

    def submit_task(self, session_id: str, capability: str, task_text: str) -> dict[str, Any]:
        """Record an advisory task; intentionally does not dispatch to an agent."""
        try:
            session = self.sessions.get(session_id)
            if session.status != "active":
                raise PermissionError("Session is not active")
            if capability in FORBIDDEN_CAPABILITIES or capability not in session.granted_capabilities:
                raise PermissionError("Capability not granted")
            if not task_text.strip() or len(task_text) > 20_000:
                raise PermissionError("Task must contain 1-20000 characters")
            task_hash = hashlib.sha256(task_text.encode()).hexdigest()
            self.audit.append("ADVISORY_TASK_ACCEPTED", agent_id=session.agent_id,
                              session_id=session_id, capability=capability,
                              task_sha256=task_hash, task_length=len(task_text),
                              dispatch_performed=False, external_effects=0)
            return {"status": "recorded_for_supervised_advisory", "task_sha256": task_hash,
                    "dispatch_performed": False, "external_effects": 0}
        except PermissionError as exc:
            self.audit.append("ADVISORY_TASK_DENIED", session_id=session_id,
                              capability=capability, reason=str(exc),
                              dispatch_performed=False, external_effects=0)
            return {"status": "denied", "reason": str(exc), "external_effects": 0}

    @staticmethod
    def _view(s: AgentSession) -> dict[str, Any]:
        return {"session_id": s.session_id, "agent_id": s.agent_id, "provider": s.provider,
                "status": s.status, "requested_capabilities": sorted(s.requested_capabilities),
                "granted_capabilities": sorted(s.granted_capabilities), "approved_by": s.approved_by,
                "token_expires_at": s.token_expires_at, "external_effects": 0}
