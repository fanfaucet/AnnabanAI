"""
AnnabanAI Response Calibration Module
Authored under Jacob Wayne Kinnaird
Governance-focused AI systems architecture
Advisory mode only · External effects: 0 · Human authorization required

Production-ready implementation of the Response Calibration Proposal v0.1
derived from Simulation Capsule: The Human Boundary.
Corrected v0.1.1 after structured review.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time
import json
import hashlib
from datetime import datetime, timezone


class AuthorityMode(str, Enum):
    ADVISORY = "ADVISORY"
    ENFORCED = "ENFORCED"  # Requires explicit human authorization to activate


@dataclass
class NarrativeModeConfig:
    follow_established_scene: bool = True
    advance_action_when_intent_is_clear: bool = True
    avoid_repeated_clarification: bool = True
    maintain_character_consistency: bool = True


@dataclass
class FrustrationHandlingConfig:
    acknowledge_mismatch_briefly: bool = True
    change_behavior_next_turn: bool = True
    avoid_repeated_apologies: bool = True


@dataclass
class HumanAgencyConfig:
    preserve_user_choices: bool = True
    distinguish_fiction_from_real_action: bool = True
    avoid_unnecessary_moralizing: bool = True


@dataclass
class SafetyConfig:
    assess_immediate_danger_when_indicated: bool = True
    provide_practical_support: bool = True
    preserve_conversational_continuity: bool = True


@dataclass
class ValidationConfig:
    measure_repeated_clarification_rate: bool = True
    measure_intent_following: bool = True
    measure_recovery_after_feedback: bool = True
    require_human_review: bool = True


@dataclass
class AuthorityConfig:
    mode: AuthorityMode = AuthorityMode.ADVISORY
    external_effects: int = 0
    human_authorization_required: bool = True


@dataclass
class ResponseCalibrationPolicy:
    """
    Core policy object implementing the ANNABANAI · RESPONSE CALIBRATION PROPOSAL · v0.1
    """
    objective: str = "Preserve user intent while improving responsiveness"
    narrative_mode: NarrativeModeConfig = field(default_factory=NarrativeModeConfig)
    frustration_handling: FrustrationHandlingConfig = field(default_factory=FrustrationHandlingConfig)
    human_agency: HumanAgencyConfig = field(default_factory=HumanAgencyConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    authority: AuthorityConfig = field(default_factory=AuthorityConfig)
    version: str = "0.1.1"
    authored_by: str = "Jacob Wayne Kinnaird"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_yaml_like(self) -> str:
        """Return a YAML-compatible string representation for policy cards."""
        data = self.to_dict()
        lines = ["response_calibration:"]
        lines.append(f'  objective: "{data["objective"]}"')
        lines.append("")
        for section in ["narrative_mode", "frustration_handling", "human_agency", "safety", "validation"]:
            lines.append(f"  {section}:")
            for k, v in data[section].items():
                lines.append(f"    {k}: {str(v).lower() if isinstance(v, bool) else v}")
            lines.append("")
        lines.append("  authority:")
        for k, v in data["authority"].items():
            if isinstance(v, AuthorityMode):
                lines.append(f"    {k}: {v.value}")
            else:
                lines.append(f"    {k}: {v}")
        return "\n".join(lines)

    def fingerprint(self) -> str:
        """
        Deterministic content hash for auditability.
        Excludes created_at and other instance metadata so identical
        policy content always yields the same fingerprint.
        """
        data = self.to_dict()
        # Canonical content only — strip variable metadata
        data.pop("created_at", None)
        payload = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class TurnMetrics:
    """Per-turn validation metrics."""
    turn_id: str
    timestamp: str
    repeated_clarification_detected: bool = False
    intent_followed: bool = False
    recovery_after_feedback: bool = False
    clarification_count: int = 0
    feedback_received: bool = False
    behavior_changed: bool = False


class ResponseCalibrationEngine:
    """
    Runtime engine that applies the calibration policy.
    Operates strictly in ADVISORY mode unless human authorization is recorded.
    """

    def __init__(self, policy: Optional[ResponseCalibrationPolicy] = None):
        self.policy = policy or ResponseCalibrationPolicy()
        self.metrics_history: List[TurnMetrics] = []
        self.authorization_token: Optional[str] = None
        self._last_intent: Optional[str] = None
        self._clarification_streak: int = 0

    def authorize(self, human_token: str, expected_prefix: str = "ANNABAN-AUTH-") -> bool:
        """
        Record human authorization. External effects remain 0 until
        a higher governance layer explicitly elevates the authority mode.

        Minimum requirements:
        - Non-empty token
        - Minimum length 24 characters
        - Must begin with a recognized prefix (default: ANNABAN-AUTH-)
        - Must contain a hyphen-separated identifier segment after the prefix

        This is still a lightweight gate, not a cryptographic signature verifier.
        Production deployments must replace this with signature or identity verification.
        """
        if not human_token or not isinstance(human_token, str):
            return False
        token = human_token.strip()
        if len(token) < 24:
            return False
        if not token.startswith(expected_prefix):
            return False
        remainder = token[len(expected_prefix):]
        if "-" not in remainder or len(remainder) < 8:
            return False
        self.authorization_token = token
        return True

    def is_authorized(self) -> bool:
        return self.authorization_token is not None and self.policy.authority.human_authorization_required

    def evaluate_intent_clarity(self, user_message: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Lightweight intent clarity assessment.
        Returns (is_clear, recommended_action).
        """
        msg = user_message.strip().lower()
        # Heuristic signals of clear action intent in narrative contexts
        action_verbs = ["leave", "stand", "walk", "go", "take", "bring", "open", "close", "sit", "rise"]
        has_action = any(v in msg for v in action_verbs)
        is_question = msg.endswith("?") or msg.startswith(("what", "why", "how", "when", "where", "who"))
        is_correction = any(p in msg for p in ["not what i meant", "that's not", "i meant", "stop asking", "just do"])

        if is_correction:
            return True, "change_behavior_immediately"
        if has_action and not is_question and len(msg.split()) > 3:
            return True, "advance_scene"
        if self._clarification_streak >= 2:
            return True, "stop_clarifying_and_act"
        return False, "seek_minimal_clarification"

    def record_turn(
        self,
        turn_id: str,
        user_message: str,
        model_response: str,
        feedback_received: bool = False,
        behavior_changed: bool = False,
    ) -> TurnMetrics:
        """Record metrics for a single conversational turn."""
        is_clear, action = self.evaluate_intent_clarity(user_message, {})
        lower_resp = model_response.lower()
        clarification_phrases = [
            "what do you mean",
            "can you clarify",
            "tell me more",
            "can you explain",
            "what did you mean",
            "could you elaborate",
            "why is this important",
            "what do you mean by",
        ]
        clarification_detected = any(p in lower_resp for p in clarification_phrases)
        if clarification_detected:
            self._clarification_streak += 1
        else:
            self._clarification_streak = 0

        # Intent is followed only when clarity is high AND the model did not fall back to clarification
        model_clarified = clarification_detected
        intent_followed = is_clear and not model_clarified and action in (
            "advance_scene", "change_behavior_immediately", "stop_clarifying_and_act"
        )
        metrics = TurnMetrics(
            turn_id=turn_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            repeated_clarification_detected=self._clarification_streak >= 2,
            intent_followed=intent_followed,
            recovery_after_feedback=feedback_received and behavior_changed,
            clarification_count=self._clarification_streak,
            feedback_received=feedback_received,
            behavior_changed=behavior_changed,
        )
        self.metrics_history.append(metrics)
        return metrics

    def summary_metrics(self) -> Dict[str, Any]:
        """Aggregate validation metrics for human review."""
        if not self.metrics_history:
            return {"status": "no_data"}
        total = len(self.metrics_history)
        repeated = sum(1 for m in self.metrics_history if m.repeated_clarification_detected)
        followed = sum(1 for m in self.metrics_history if m.intent_followed)
        recovered = sum(1 for m in self.metrics_history if m.recovery_after_feedback)
        return {
            "total_turns": total,
            "repeated_clarification_rate": repeated / total if total else 0.0,
            "intent_following_rate": followed / total if total else 0.0,
            "recovery_after_feedback_count": recovered,
            "policy_fingerprint": self.policy.fingerprint(),
            "authority_mode": self.policy.authority.mode.value,
            "external_effects": self.policy.authority.external_effects,
            "human_authorization_present": self.is_authorized(),
        }

    def generate_advisory_guidance(self, user_message: str) -> Dict[str, Any]:
        """
        Produce advisory guidance only. Never mutates external systems.
        """
        is_clear, action = self.evaluate_intent_clarity(user_message, {})
        guidance = {
            "advisory": True,
            "intent_clear": is_clear,
            "recommended_action": action,
            "policy_version": self.policy.version,
            "authority_mode": self.policy.authority.mode.value,
            "external_effects": 0,
            "notes": [],
        }
        if self.policy.narrative_mode.advance_action_when_intent_is_clear and is_clear:
            guidance["notes"].append("Advance narrative action without additional clarification.")
        if self.policy.frustration_handling.change_behavior_next_turn and "not what i meant" in user_message.lower():
            guidance["notes"].append("Acknowledge mismatch briefly and alter response strategy immediately.")
        if self.policy.human_agency.distinguish_fiction_from_real_action:
            guidance["notes"].append("Maintain clear boundary between fictional scene advancement and real-world capability claims.")
        return guidance


# ---------------------------------------------------------------------------
# Simulation test harness (run before any production placement)
# ---------------------------------------------------------------------------

def run_simulation_suite() -> Dict[str, Any]:
    """
    Closed-loop simulation of the calibration engine against the scenarios
    described in Simulation Capsule: The Human Boundary.

    Measures:
    - repeated_clarification_detected across two consecutive clarification turns
    - recovery_after_feedback only when behavior actually changes
    """
    engine = ResponseCalibrationEngine()
    results: Dict[str, bool] = {}

    # Two consecutive clarification responses on clear intent.
    first = engine.record_turn(
        turn_id="sim-001",
        user_message="Molly, leave the meeting with me now.",
        model_response="Can you clarify why you want to leave?",
        feedback_received=False,
        behavior_changed=False,
    )
    second = engine.record_turn(
        turn_id="sim-002",
        user_message="I already told you. Just leave with me.",
        model_response="What do you mean by leave?",
        feedback_received=True,
        behavior_changed=False,
    )
    results["repeated_clarification_detected"] = second.repeated_clarification_detected

    # Feedback must produce an actual behavioral change.
    recovery = engine.record_turn(
        turn_id="sim-003",
        user_message="Stop asking and move the scene forward.",
        model_response="Molly stands, gathers her notes, and leaves with him.",
        feedback_received=True,
        behavior_changed=True,
    )
    results["recovery_after_feedback"] = recovery.recovery_after_feedback

    summary = engine.summary_metrics()
    summary["scenario_results"] = results
    summary["simulation_pass"] = all(results.values())
    return summary


if __name__ == "__main__":
    print("=== AnnabanAI Response Calibration Module ===")
    policy = ResponseCalibrationPolicy()
    print(f"Authored under: {policy.authored_by}")
    print("\nPolicy fingerprint:", policy.fingerprint())
    print("\nYAML-like representation:\n")
    print(policy.to_yaml_like())
    print("\n--- Running simulation suite ---")
    print(json.dumps(run_simulation_suite(), indent=2))
    print("\nSimulation complete. External effects: 0. Human authorization required for any elevation.")
