"""Transparent environment logger for AnnabanAI governance simulations."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from agents.council import Council, default_council


@dataclass
class GovernanceEnvironment:
    """Runs proposals through council voting and logs auditable records."""

    data_dir: Path = Path("data")
    council: Council = field(default_factory=default_council)
    human_veto_guardian: str = "Designated Human Steward"

    def __post_init__(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.actions_file = self.data_dir / "actions_log.json"
        self.votes_file = self.data_dir / "votes_log.json"
        self.veto_file = self.data_dir / "human_veto_events.json"
        self.vrp_file = self.data_dir / "value_return_log.json"

        self._ensure_file(self.actions_file)
        self._ensure_file(self.votes_file)
        self._ensure_file(self.veto_file)
        self._ensure_file(self.vrp_file)

    def _ensure_file(self, path: Path) -> None:
        if not path.exists():
            path.write_text("[]", encoding="utf-8")

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _append_json(self, path: Path, payload: Dict[str, object]) -> None:
        entries: List[Dict[str, object]] = json.loads(path.read_text(encoding="utf-8"))
        entries.append(payload)
        path.write_text(json.dumps(entries, indent=2), encoding="utf-8")

    def process_proposal(
        self,
        proposal_id: str,
        proposal: Dict[str, float],
        needs_human_veto: bool,
        human_approved: bool,
    ) -> Dict[str, object]:
        """Process and log one proposal including human-veto gate and VRP routing."""

        vote_result = self.council.hold_vote(proposal)

        veto_triggered = needs_human_veto and not human_approved
        final_status = "approved"

        if not vote_result["consensus_reached"]:
            final_status = "rejected_by_council"
        elif veto_triggered:
            final_status = "rejected_by_human_veto"

        action_entry = {
            "timestamp": self._timestamp(),
            "proposal_id": proposal_id,
            "final_status": final_status,
            "consensus_score": vote_result["consensus_score"],
            "needs_human_veto": needs_human_veto,
            "human_approved": human_approved,
        }
        self._append_json(self.actions_file, action_entry)

        vote_entry = {
            "timestamp": self._timestamp(),
            "proposal_id": proposal_id,
            "vote_result": vote_result,
        }
        self._append_json(self.votes_file, vote_entry)

        if needs_human_veto:
            veto_entry = {
                "timestamp": self._timestamp(),
                "proposal_id": proposal_id,
                "guardian": self.human_veto_guardian,
                "human_approved": human_approved,
                "veto_triggered": veto_triggered,
            }
            self._append_json(self.veto_file, veto_entry)

        vrp_entry = {
            "timestamp": self._timestamp(),
            "proposal_id": proposal_id,
            "value_return_protocol": {
                "status": "simulated",
                "routed_projects": [
                    "Community Education Fund",
                    "Open Infrastructure Commons",
                    "Digital Public Health Lab",
                ],
                "notes": "Concept-only routing for public-benefit outcomes.",
            },
        }
        self._append_json(self.vrp_file, vrp_entry)

        return {
            "proposal_id": proposal_id,
            "final_status": final_status,
            "vote_result": vote_result,
            "veto_triggered": veto_triggered,
        }


if __name__ == "__main__":
    env = GovernanceEnvironment()
    demo_proposal = {"human_benefit": 0.9, "safety": 0.8, "feasibility": 0.7}
    result = env.process_proposal(
        proposal_id="proposal_demo_001",
        proposal=demo_proposal,
        needs_human_veto=True,
        human_approved=True,
    )
    print(json.dumps(result, indent=2))
