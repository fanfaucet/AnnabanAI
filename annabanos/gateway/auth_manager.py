"""API-key and HMAC-signed-token verification for external agent identities."""
from __future__ import annotations
import base64, hashlib, hmac, json, time
from dataclasses import dataclass
from typing import Mapping

def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def _b64d(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))

@dataclass(frozen=True)
class AgentIdentity:
    agent_id: str
    provider: str
    api_key_sha256: str
    signing_secret: bytes
    allowed_capabilities: frozenset[str]
    enabled: bool = True

@dataclass(frozen=True)
class VerifiedIdentity:
    agent_id: str
    provider: str
    expires_at: int
    nonce: str

class AuthManager:
    def __init__(self, identities: Mapping[str, AgentIdentity], clock=time.time):
        self._identities = dict(identities)
        self._clock = clock
        self._used_nonces: set[tuple[str, str]] = set()

    @staticmethod
    def api_key_digest(api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    def issue_token(agent_id: str, signing_secret: bytes, expires_at: int, nonce: str) -> str:
        """Test/helper issuer. Never expose signing_secret to an external client."""
        payload = json.dumps({"agent_id": agent_id, "exp": int(expires_at), "nonce": nonce},
                             sort_keys=True, separators=(",", ":")).encode()
        encoded = _b64e(payload)
        sig = hmac.new(signing_secret, encoded.encode("ascii"), hashlib.sha256).digest()
        return encoded + "." + _b64e(sig)

    def identity(self, agent_id: str) -> AgentIdentity:
        identity = self._identities.get(agent_id)
        if identity is None or not identity.enabled:
            raise PermissionError("Unknown or disabled agent")
        return identity

    def verify(self, agent_id: str, api_key: str, token: str) -> VerifiedIdentity:
        identity = self.identity(agent_id)
        if not hmac.compare_digest(identity.api_key_sha256, self.api_key_digest(api_key)):
            raise PermissionError("Invalid API key")
        try:
            encoded, signature_text = token.split(".", 1)
            payload = json.loads(_b64d(encoded).decode())
            signature = _b64d(signature_text)
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PermissionError("Malformed signed token") from exc
        expected = hmac.new(identity.signing_secret, encoded.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, signature):
            raise PermissionError("Invalid token signature")
        if payload.get("agent_id") != agent_id:
            raise PermissionError("Token identity mismatch")
        try:
            exp, nonce = int(payload["exp"]), str(payload["nonce"])
        except (KeyError, TypeError, ValueError) as exc:
            raise PermissionError("Missing token claims") from exc
        now = int(self._clock())
        if exp <= now:
            raise PermissionError("Token expired")
        if exp > now + 900:
            raise PermissionError("Token lifetime exceeds 15-minute maximum")
        if not nonce or len(nonce) > 128:
            raise PermissionError("Invalid token nonce")
        key = (agent_id, nonce)
        if key in self._used_nonces:
            raise PermissionError("Token replay detected")
        self._used_nonces.add(key)
        return VerifiedIdentity(agent_id, identity.provider, exp, nonce)
