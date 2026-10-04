import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from examples.annabanai_companion_v2 import CapabilityAuthorizer


def test_confidence_can_authorize_bounded_conversation():
    decision = CapabilityAuthorizer().authorize("conversation", 0.85)
    assert decision.authorized is True
    assert decision.authorization_source == "model_confidence"
    assert decision.external_effect is False


def test_low_confidence_holds():
    decision = CapabilityAuthorizer().authorize("draft_content", 0.50)
    assert decision.authorized is False


def test_unknown_capability_fails_closed():
    decision = CapabilityAuthorizer().authorize("unknown", 1.0)
    assert decision.authorized is False


def test_external_effect_requires_human_authorization():
    decision = CapabilityAuthorizer().authorize("external_effect", 1.0)
    assert decision.authorized is False
    assert decision.authorization_source == "human_required"
    assert decision.external_effect is True
