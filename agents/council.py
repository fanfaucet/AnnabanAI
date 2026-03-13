"""Council simulation for AnnabanAI governance experiments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from agents.base_agent import BaseAgent


@dataclass
class Council:
    """A council of agents that evaluates proposals and computes consensus."""

    agents: List[BaseAgent]
    consensus_threshold: float = 0.67

    def hold_vote(self, proposal: Dict[str, float]) -> Dict[str, object]:
        """Run a vote and compute a consensus score from member evaluations."""

        evaluations = [agent.evaluate_proposal(proposal) for agent in self.agents]
        approvals = [item for item in evaluations if item["vote"] == "approve"]

        approval_ratio = len(approvals) / len(self.agents) if self.agents else 0.0
        average_score = (
            sum(float(item["score"]) for item in evaluations) / len(evaluations)
            if evaluations
            else 0.0
        )

        consensus_score = round((approval_ratio * 0.6) + (average_score * 0.4), 4)
        consensus_reached = consensus_score >= self.consensus_threshold

        return {
            "evaluations": evaluations,
            "approval_ratio": round(approval_ratio, 4),
            "average_score": round(average_score, 4),
            "consensus_score": consensus_score,
            "consensus_reached": consensus_reached,
        }


def default_council() -> Council:
    """Create a default council for demo use."""

    return Council(
        agents=[
            BaseAgent(name="Ada", role="Safety Steward"),
            BaseAgent(name="Lin", role="Public Benefit Analyst"),
            BaseAgent(name="Noor", role="Implementation Reviewer"),
        ]
    )
