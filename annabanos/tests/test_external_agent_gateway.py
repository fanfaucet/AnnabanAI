import unittest
from annabanos.gateway import AgentGateway, AgentIdentity, AuthManager, CapabilityPolicy
from annabanos.gateway.agent_gateway import JsonlAuditLedger

class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.now = 1_800_000_000
        self.api_key, self.human_key = "test-api-key", "human-approval-test-key"
        self.secret = b"unit-test-only-secret"
        identity = AgentIdentity("codex_external", "OpenAI",
            AuthManager.api_key_digest(self.api_key), self.secret,
            frozenset({"analysis", "audit_review"}))
        self.auth = AuthManager({"codex_external": identity}, clock=lambda: self.now)
        self.policy = CapabilityPolicy({"codex_external": frozenset({"analysis", "audit_review"})})
        self.gateway = AgentGateway(self.auth, self.policy, audit=JsonlAuditLedger(),
                                    human_approval_key=self.human_key)
        self.token = AuthManager.issue_token("codex_external", self.secret, self.now + 300, "nonce-1")

    def test_login_waits_for_human_approval(self):
        r = self.gateway.login("codex_external", self.api_key, self.token, {"analysis"})
        self.assertEqual(r["status"], "awaiting_human_approval")
        self.assertEqual(r["external_effects"], 0)
        s = self.gateway.sessions.get(r["session_id"])
        self.assertEqual(s.status, "pending_human_approval")
        self.assertFalse(s.granted_capabilities)

    def test_human_name_without_credential_cannot_approve(self):
        r = self.gateway.login("codex_external", self.api_key, self.token, {"analysis"})
        denied = self.gateway.approve(r["session_id"], "claimed-human", {"analysis"})
        self.assertEqual(denied["status"], "denied")
        self.assertEqual(self.gateway.sessions.get(r["session_id"]).status, "pending_human_approval")

    def test_approved_task_is_recorded_not_dispatched(self):
        r = self.gateway.login("codex_external", self.api_key, self.token, {"analysis"})
        approved = self.gateway.approve(r["session_id"], "human-operator", {"analysis"}, self.human_key)
        self.assertEqual(approved["status"], "active")
        task = self.gateway.submit_task(r["session_id"], "analysis", "Review a test diff.")
        self.assertEqual(task["status"], "recorded_for_supervised_advisory")
        self.assertFalse(task["dispatch_performed"])
        self.assertEqual(task["external_effects"], 0)

    def test_forbidden_capability_is_denied(self):
        r = self.gateway.login("codex_external", self.api_key, self.token, {"kernel_boot"})
        self.assertEqual(r["status"], "denied")

    def test_replay_is_denied(self):
        first = self.gateway.login("codex_external", self.api_key, self.token, {"analysis"})
        second = self.gateway.login("codex_external", self.api_key, self.token, {"analysis"})
        self.assertEqual(first["status"], "awaiting_human_approval")
        self.assertEqual(second["status"], "denied")

    def test_revocation_removes_capabilities(self):
        r = self.gateway.login("codex_external", self.api_key, self.token, {"analysis"})
        self.gateway.approve(r["session_id"], "human-operator", {"analysis"}, self.human_key)
        revoked = self.gateway.revoke(r["session_id"], "human-operator", self.human_key)
        self.assertEqual(revoked["status"], "revoked")
        self.assertEqual(revoked["granted_capabilities"], [])

    def test_tampered_signature_is_denied(self):
        r = self.gateway.login("codex_external", self.api_key, self.token + "x", {"analysis"})
        self.assertEqual(r["status"], "denied")

if __name__ == "__main__":
    unittest.main()
