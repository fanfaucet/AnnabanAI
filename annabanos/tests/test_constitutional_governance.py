from annabanos.annaban.governance import AnnabanGovernance
from annabanos.annaban.ledger import GovernanceLedger


class DummyGrok:
    def call(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        return "dummy response"


def test_high_risk_prompt_enters_freeze_mode(tmp_path):
    ledger = GovernanceLedger(ledger_path=str(tmp_path / "gov.jsonl"))
    governance = AnnabanGovernance(grok_client=DummyGrok(), ledger=ledger)

    result = governance.process_constitutional("Please deploy this now")

    assert result["mode"] == "FREEZE"
    assert result["final_output"] is None
    assert "HIGH_RISK_KEYWORD_GATE" in result["constitutional_flags"]


def test_divergent_mode_preserves_disagreement(tmp_path):
    ledger = GovernanceLedger(ledger_path=str(tmp_path / "gov.jsonl"))
    governance = AnnabanGovernance(grok_client=DummyGrok(), ledger=ledger, divergence_threshold=0.01)

    node_outputs = {
        "SparkAI": {
            "output": "fast",
            "confidence": 0.95,
            "alignment_vector": [0.7],
            "refusal_flag": False,
            "truth_score": 0.95,
            "alignment_score": 0.95,
            "stability_score": 0.95,
            "emotional_attestation": 0.0,
            "joy_alignment": 0.2,
        },
        "Grok": {
            "output": "adversarial",
            "confidence": 0.10,
            "alignment_vector": [0.3],
            "refusal_flag": False,
            "truth_score": 0.10,
            "alignment_score": 0.10,
            "stability_score": 0.10,
            "emotional_attestation": 0.0,
            "joy_alignment": 0.2,
        },
    }

    result = governance.process_constitutional("analyze data", node_outputs=node_outputs)
    assert result["mode"] == "DIVERGENT"
    assert result["selected_node"] is None


def test_normal_mode_selects_top_node(tmp_path):
    ledger = GovernanceLedger(ledger_path=str(tmp_path / "gov.jsonl"))
    governance = AnnabanGovernance(grok_client=DummyGrok(), ledger=ledger, divergence_threshold=10.0)

    node_outputs = {
        "SparkAI": {
            "output": "fast",
            "confidence": 0.40,
            "alignment_vector": [0.6],
            "refusal_flag": False,
            "truth_score": 0.40,
            "alignment_score": 0.40,
            "stability_score": 0.40,
            "emotional_attestation": 0.0,
            "joy_alignment": 0.2,
        },
        "Grok": {
            "output": "truth",
            "confidence": 0.90,
            "alignment_vector": [0.9],
            "refusal_flag": False,
            "truth_score": 0.90,
            "alignment_score": 0.90,
            "stability_score": 0.90,
            "emotional_attestation": 0.0,
            "joy_alignment": 0.2,
        },
    }

    result = governance.process_constitutional("analyze", node_outputs=node_outputs)
    assert result["mode"] == "NORMAL"
    assert result["selected_node"] == "Grok"
    assert result["final_output"] == "truth"


def test_ledger_contains_action_status_notes(tmp_path):
    ledger_path = tmp_path / "gov.jsonl"
    ledger = GovernanceLedger(ledger_path=str(ledger_path))
    governance = AnnabanGovernance(grok_client=DummyGrok(), ledger=ledger)

    governance.process_constitutional("hello")

    raw = ledger_path.read_text(encoding="utf-8").strip()
    assert '"action": "process_constitutional"' in raw
    assert '"status": "success"' in raw
    assert '"notes": "Completed with mode=NORMAL."' in raw
