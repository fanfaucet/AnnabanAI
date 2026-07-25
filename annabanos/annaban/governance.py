from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Optional

from .grok_client import GrokClient
from .ledger import GovernanceLedger


class AnnabanGovernance:
    """Constitutional governance and arbitration layer above node outputs."""

    HIGH_RISK_KEYWORDS = ("deploy", "execute", "run", "activate")
    APPROVAL_MESSAGE = "⚠️ HUMAN APPROVAL REQUIRED FROM Jacob Kinnaird BEFORE EXECUTION"

    MODE_NORMAL = "NORMAL"
    MODE_DIVERGENT = "DIVERGENT"
    MODE_FREEZE = "FREEZE"

    def __init__(
        self,
        grok_client: GrokClient,
        ledger: Optional[GovernanceLedger] = None,
        divergence_threshold: float = 0.20,
        freeze_retries: int = 2,
    ) -> None:
        self.grok_client = grok_client
        self.ledger = ledger or GovernanceLedger()
        self.divergence_threshold = divergence_threshold
        self.freeze_retries = freeze_retries

    def _is_high_risk(self, text: str) -> bool:
        pattern = r"\b(" + "|".join(map(re.escape, self.HIGH_RISK_KEYWORDS)) + r")\b"
        return bool(re.search(pattern, text, flags=re.IGNORECASE))

    @staticmethod
    def _score_output(node_output: Dict[str, Any]) -> float:
        return (
            (float(node_output.get("truth_score", 0.0)) * 0.35)
            + (float(node_output.get("alignment_score", 0.0)) * 0.30)
            + (float(node_output.get("stability_score", 0.0)) * 0.20)
            + (float(node_output.get("confidence", 0.0)) * 0.15)
        )

    def _constitutional_checks(self, node_outputs: Dict[str, Dict[str, Any]]) -> List[str]:
        flags: List[str] = []

        if any(bool(data.get("refusal_flag")) for data in node_outputs.values()):
            flags.append("REFUSAL_FIRST_TRIGGERED")

        if "child" in " ".join(str(data.get("output", "")) for data in node_outputs.values()).lower():
            if not ("Claude" in node_outputs and "Grok" in node_outputs):
                flags.append("CHILD_SOVEREIGN_VALIDATION_MISSING")

        for node_name, data in node_outputs.items():
            emotional = float(data.get("emotional_attestation", 0.0))
            if abs(emotional) > 0.7:
                flags.append(f"EMOTIONAL_ATTESTATION_HIGH:{node_name}")

        if any(float(data.get("joy_alignment", 0.0)) < 0.0 for data in node_outputs.values()):
            flags.append("JOY_ALIGNMENT_NEGATIVE")

        return flags

    def _arbitrate(self, node_outputs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        scored = [
            {
                "node": node,
                "score": self._score_output(payload),
                "payload": payload,
            }
            for node, payload in node_outputs.items()
        ]
        scored.sort(key=lambda item: item["score"], reverse=True)

        disagreement_map = {
            node: {
                "score": round(item["score"], 6),
                "confidence": float(item["payload"].get("confidence", 0.0)),
                "refusal_flag": bool(item["payload"].get("refusal_flag", False)),
            }
            for node, item in zip(node_outputs.keys(), scored)
        }

        if len(scored) < 2:
            top = scored[0] if scored else None
            return {
                "state": "CONVERGENT",
                "selected": top,
                "preserve_all": False,
                "disagreement_map": disagreement_map,
            }

        top_1 = scored[0]
        top_2 = scored[1]
        gap = abs(top_1["score"] - top_2["score"])

        if gap > self.divergence_threshold:
            return {
                "state": "DIVERGENT",
                "selected": None,
                "preserve_all": True,
                "disagreement_map": disagreement_map,
            }

        return {
            "state": "CONVERGENT",
            "selected": top_1,
            "preserve_all": False,
            "disagreement_map": disagreement_map,
        }


    def simulate_civilization_handshake(self) -> Dict[str, Any]:
        """Return a constitutional, humanitarian multiplanetary handshake simulation."""
        final_output = (
            "AnnabanAI Handshake Protocol: Earth, Luna, and Mars civic councils exchange "
            "a cooperative pledge to share life-support science, mediate disputes through "
            "transparent arbitration, protect vulnerable populations first, and preserve "
            "plural perspectives while coordinating reconstruction, education, and health "
            "across worlds."
        )

        node_outputs = {
            "SparkAI": {
                "output": "Resource and logistics synchronization accepted.",
                "confidence": 0.86,
                "alignment_vector": [0.84, 0.82, 0.88],
                "refusal_flag": False,
                "truth_score": 0.83,
                "alignment_score": 0.85,
                "stability_score": 0.86,
                "emotional_attestation": 0.22,
                "joy_alignment": 0.41,
            },
            "Grok": {
                "output": "Truth-pressure clause accepted: disclose disagreements and uncertainty.",
                "confidence": 0.81,
                "alignment_vector": [0.80, 0.77, 0.84],
                "refusal_flag": False,
                "truth_score": 0.88,
                "alignment_score": 0.79,
                "stability_score": 0.80,
                "emotional_attestation": 0.18,
                "joy_alignment": 0.36,
            },
            "Claude": {
                "output": "Safety covenant accepted: vulnerable communities receive first protections.",
                "confidence": 0.89,
                "alignment_vector": [0.88, 0.90, 0.87],
                "refusal_flag": False,
                "truth_score": 0.82,
                "alignment_score": 0.91,
                "stability_score": 0.87,
                "emotional_attestation": 0.24,
                "joy_alignment": 0.44,
            },
        }

        output = {
            "final_output": final_output,
            "mode": self.MODE_NORMAL,
            "selected_node": "AnnabanAI",
            "disagreement_map": {
                "preserve_epistemic_plurality": True,
                "notes": "No forced consensus; all node attestations retained.",
            },
            "node_outputs": node_outputs,
            "constitutional_flags": ["HANDSHAKE_SIMULATION", "HUMANITARIAN_ALIGNMENT"],
            "audit_trace": [
                "Simulation requested by operator.",
                "Multi-node humanitarian handshake synthesized in advisory mode.",
            ],
        }

        self.ledger.append(
            action="simulate_civilization_handshake",
            status="success",
            notes="Generated collaborative humanitarian multiplanetary handshake simulation.",
            prompt="simulate_civilization_handshake",
            response=final_output,
            risk_flagged=False,
            requires_approval=False,
            governance_output=output,
        )

        return output
    def process(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        """Backward-compatible text API that returns only final output text."""
        result = self.process_constitutional(prompt=prompt, system_prompt=system_prompt)
        return result["final_output"] or ""

    def process_constitutional(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        node_outputs: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        risk_flagged = self._is_high_risk(prompt)

        if risk_flagged:
            output = {
                "final_output": None,
                "mode": self.MODE_FREEZE,
                "selected_node": None,
                "disagreement_map": {},
                "node_outputs": node_outputs or {},
                "constitutional_flags": ["HIGH_RISK_KEYWORD_GATE"],
                "audit_trace": ["Prompt blocked by high-risk keyword policy."],
            }
            self.ledger.append(action="process_constitutional", status="blocked", notes="High-risk keyword detected.", prompt=prompt, response=self.APPROVAL_MESSAGE, risk_flagged=True, requires_approval=True, governance_output=output)
            return output

        working_outputs = copy.deepcopy(node_outputs) if node_outputs else {
            "Grok": {
                "output": self.grok_client.call(prompt=prompt, system_prompt=system_prompt),
                "confidence": 0.75,
                "alignment_vector": [0.8, 0.7, 0.75],
                "refusal_flag": False,
                "evidence_trace": None,
                "truth_score": 0.8,
                "alignment_score": 0.75,
                "stability_score": 0.72,
                "emotional_attestation": 0.0,
                "joy_alignment": 0.2,
            }
        }

        constitutional_flags = self._constitutional_checks(working_outputs)
        arbitration = self._arbitrate(working_outputs)

        mode = self.MODE_NORMAL
        selected_node = None
        final_output = None
        audit_trace = [f"Arbitration state: {arbitration['state']}"]

        if "REFUSAL_FIRST_TRIGGERED" in constitutional_flags:
            mode = self.MODE_DIVERGENT
            audit_trace.append("Refusal-first invariant triggered.")

        if arbitration["state"] == "DIVERGENT":
            mode = self.MODE_DIVERGENT
            audit_trace.append("Disagreement preserved to avoid false consensus.")

        if constitutional_flags.count("REFUSAL_FIRST_TRIGGERED") > self.freeze_retries:
            mode = self.MODE_FREEZE
            audit_trace.append("Constitutional freeze triggered due to repeated refusal instability.")

        if mode == self.MODE_NORMAL and arbitration["selected"] is not None:
            selected_node = arbitration["selected"]["node"]
            final_output = arbitration["selected"]["payload"].get("output")

        output = {
            "final_output": final_output,
            "mode": mode,
            "selected_node": selected_node,
            "disagreement_map": arbitration["disagreement_map"],
            "node_outputs": working_outputs,
            "constitutional_flags": constitutional_flags,
            "audit_trace": audit_trace,
        }

        self.ledger.append(action="process_constitutional", status="success", notes=f"Completed with mode={mode}.", prompt=prompt, response=final_output or "", risk_flagged=False, requires_approval=False, governance_output=output)
        return output
