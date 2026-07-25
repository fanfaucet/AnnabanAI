from annabanos.annaban.governance import AnnabanGovernance
from annabanos.annaban.ledger import GovernanceLedger


class DummyGrok:
    def call(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        return "dummy response"


def test_simulate_civilization_handshake_shape_and_mode(tmp_path):
    ledger = GovernanceLedger(ledger_path=str(tmp_path / "gov.jsonl"))
    governance = AnnabanGovernance(grok_client=DummyGrok(), ledger=ledger)

    output = governance.simulate_civilization_handshake()

    assert output["mode"] == "NORMAL"
    assert output["selected_node"] == "AnnabanAI"
    assert "HANDSHAKE_SIMULATION" in output["constitutional_flags"]
    assert "HUMANITARIAN_ALIGNMENT" in output["constitutional_flags"]
    assert "Earth, Luna, and Mars" in output["final_output"]
    assert set(output["node_outputs"].keys()) == {"SparkAI", "Grok", "Claude"}


def test_simulate_civilization_handshake_writes_ledger_entry(tmp_path):
    ledger_path = tmp_path / "gov.jsonl"
    ledger = GovernanceLedger(ledger_path=str(ledger_path))
    governance = AnnabanGovernance(grok_client=DummyGrok(), ledger=ledger)

    governance.simulate_civilization_handshake()

    raw = ledger_path.read_text(encoding="utf-8")
    assert '"action": "simulate_civilization_handshake"' in raw
    assert '"status": "success"' in raw
