import unittest
from annabanos.gateway import AgentGateway, AgentIdentity, AuthManager, CapabilityPolicy
from annabanos.gateway.agent_gateway import JsonlAuditLedger

class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.now = 1_800_000_000
        self.api_key = "test-api-key"
        self.secret = b"unit-test-only-secret"
        identity = AgentIdentity(
            agent_id="codex_external", provider="OpenAI",
            api_key_sha256=AuthManager.api_key_digest(self.api_key),
            signing_secret=self.secret,
            allowed_capabilities=frozenset({"analysis", "audit_review"}),
        )
        self.auth = AuthManager({"codex_external": identity}, clock=lambda: self.now)
        self.policy = CapabilityPolicy({"codex_external": frozenset({"analysis", "audit_review"})})
        self.gateway = AgentGateway(self.auth, self.policy, audit=JsonlAuditLedger())
        self.token = AuthManager.issue_token("codex_external", self.secret, self.now + 300, "nonce-1")

    def test_login_requires_human_approval_and_has_no_dispatch(self):
        response = self.gateway.login("codex_external", self.api_key, self.token, {"analysis"})
        self.assertEqual(response["status"], "awaiting_human_approval")
        self.assertEqual(response["external_effects"], 0)
        session = self.gateway.sessions.get(response["session_id"])
        self.assertEqual(session.status, "pending_human_approval")
        self.assertFalse(session.granted_capabilities)

    def test_approved_task_is_recorded_but_not_dispatched(self):
        response = self.gateway.login("codex_external", self.api_key, self.token, {"analysis"})
        approved = self.gateway.approve(response["session_id"], "human-operator", {"analysis"})
        self.assertEqual(approved["status"], "active")
        task = self.gateway.submit_task(response["session_id"], "analysis", "Review a test diff.")
        self.assertEqual(task["status"], "recorded_for_supervised_advisory")
        self.assertFalse(task["dispatch_performed"])
        self.assertEqual(task["external_effects"], 0)

    def test_forbidden_capability_is_denied(self):
        response = self.gateway.login("codex_external", self.api_key, self.token, {"kernel_boot"})
        self.assertEqual(response["status"], "denied")

    def test_replay_is_denied(self):
        first = self.gateway.login("codex_external", self.api_key, self.token, {"analysis"})
        second = self.gateway.login("codex_external", self.api_key, self.token, {"analysis"})
        self.assertEqual(first["status"], "awaiting_human_approval")
        self.assertEqual(second["status"], "denied")

    def test_revocation_removes_capabilities(self):
        response = self.gateway.login("codex_external", self.api_key, self.token, {"analysis"})
        self.gateway.approve(response["session_id"], "human-operator", {"analysis"})
        revoked = self.gateway.revoke(response["session_id"], "human-operator")
        self.assertEqual(revoked["status"], "revoked")
        self.assertEqual(revoked["granted_capabilities"], [])

    def test_tampered_signature_is_denied(self):
        response = self.gateway.login("codex_external", self.api_key, self.token + "x", {"analysis"})
        self.assertEqual(response["status"], "denied")

if __name__ == "__main__":
    unittest.main()
