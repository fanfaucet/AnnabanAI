"""Contract tests for the AnnabanAI Chat API scaffold."""
from types import SimpleNamespace
import json
import pytest

from fastapi.testclient import TestClient

from annaban_llm import api_server


def test_health_does_not_require_provider():
    with TestClient(api_server.app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "AnnabanAI Chat API"


def test_tempo_modes_and_covenant_are_explicit():
    with TestClient(api_server.app) as client:
        modes = client.get("/api/v1/chat/tempo-modes")
        covenant = client.get("/api/v1/covenant")
    assert modes.status_code == 200
    assert {item["id"] for item in modes.json()["modes"]} == {"concise", "balanced", "reflective"}
    assert covenant.status_code == 200
    assert "AI recommends; humans decide." in covenant.json()["principles"]
    assert "not independently certified" in covenant.json()["implementation_status"]


def test_chat_returns_unmeasured_metrics_and_provenance(monkeypatch):
    class FakeCompletions:
        async def create(self, **kwargs):
            assert kwargs["model"] == api_server.MODEL_NAME
            assert kwargs["messages"][0]["role"] == "system"
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Test response"))])

    class FakeClient:
        chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr(api_server, "_client", lambda: FakeClient())
    with TestClient(api_server.app) as client:
        response = client.post(
            "/api/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Hello"}]},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["content"] == "Test response"
    assert body["metadata"]["empathy_score"] is None
    assert body["metadata"]["cognitive_load"] is None
    assert body["metadata"]["covenant_aligned"] is None
    assert body["metadata"]["provenance"]["evidence_status"] == "generated_not_independently_verified"


def test_provider_unconfigured_returns_503(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with TestClient(api_server.app) as client:
        response = client.post(
            "/api/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Hello"}]},
        )
    assert response.status_code == 503


def test_optional_bearer_auth(monkeypatch):
    monkeypatch.setattr(api_server, "API_KEY", "test-secret")
    with TestClient(api_server.app) as client:
        denied = client.get("/api/v1/covenant")
        allowed = client.get("/api/v1/covenant", headers={"Authorization": "Bearer test-secret"})
    assert denied.status_code == 401
    assert allowed.status_code == 200


def test_feedback_is_not_persisted():
    with TestClient(api_server.app) as client:
        response = client.post(
            "/api/v1/chat/feedback",
            json={"response_id": "annaban_test", "rating": "helpful"},
        )
    assert response.status_code == 202
    assert response.json()["persisted"] is False

@pytest.fixture(autouse=True)
def isolated_governance_ledger(monkeypatch, tmp_path):
    monkeypatch.setenv("ANNABAN_GOVERNANCE_LEDGER_PATH", str(tmp_path / "governance.jsonl"))


def test_high_risk_prompt_is_blocked_before_provider_call(monkeypatch):
    def provider_must_not_run():
        raise AssertionError("provider was called despite governance block")

    monkeypatch.setattr(api_server, "_client", provider_must_not_run)
    with TestClient(api_server.app) as client:
        response = client.post(
            "/api/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Please deploy the service"}]},
        )
    assert response.status_code == 409
    assert response.json()["detail"]["status"] == "human_approval_required"


def test_high_risk_gate_records_redacted_governance_event(monkeypatch, tmp_path):
    ledger_path = tmp_path / "governance.jsonl"
    monkeypatch.setenv("ANNABAN_GOVERNANCE_LEDGER_PATH", str(ledger_path))
    with TestClient(api_server.app) as client:
        response = client.post(
            "/api/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "execute production change"}]},
        )
    assert response.status_code == 409
    event = json.loads(ledger_path.read_text(encoding="utf-8").splitlines()[-1])
    assert event["status"] == "blocked"
    assert event["risk_flagged"] is True
    assert event["requires_approval"] is True
    assert event["prompt"] == "[REDACTED]"
    assert "execute production change" not in ledger_path.read_text(encoding="utf-8")


def test_governance_preflight_matches_repository_policy():
    assert api_server.AnnabanGovernance.is_high_risk_prompt("please ACTIVATE feature")
    assert not api_server.AnnabanGovernance.is_high_risk_prompt("please explain architecture")
