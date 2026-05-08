"""Council simulation for AnnabanAI governance experiments."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, TypedDict

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

# Required keys in proposal dicts
REQUIRED_PROPOSAL_KEYS = {"human_benefit", "safety", "feasibility"}


class VoteResult(TypedDict):
    """Structured result of a council vote."""

    evaluations: List[Dict[str, Any]]
    approval_ratio: float
    average_score: float
    consensus_score: float
    consensus_reached: bool
    explanation: str


@dataclass
class Council:
    """A council of agents that evaluates proposals and computes consensus.

    Attributes:
        agents: List of BaseAgent instances to participate in voting.
        consensus_threshold: Score (0.0-1.0) required to reach consensus.
            Default 0.67 requires ~2/3 approval.
        consensus_weight_ratio: Weight for approval_ratio in consensus score.
            Default 0.6 means approval_ratio contributes 60%.
        consensus_weight_score: Weight for average_score in consensus score.
            Default 0.4 means average_score contributes 40%.
    """

    agents: List[BaseAgent]
    consensus_threshold: float = 0.67
    consensus_weight_ratio: float = 0.6
    consensus_weight_score: float = 0.4

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.agents:
            raise ValueError("Council must have at least one agent to hold a vote")

        if not 0.0 <= self.consensus_threshold <= 1.0:
            raise ValueError("consensus_threshold must be between 0.0 and 1.0")

        if not 0.0 <= self.consensus_weight_ratio <= 1.0:
            raise ValueError("consensus_weight_ratio must be between 0.0 and 1.0")

        if not 0.0 <= self.consensus_weight_score <= 1.0:
            raise ValueError("consensus_weight_score must be between 0.0 and 1.0")

        weight_sum = self.consensus_weight_ratio + self.consensus_weight_score
        if not (0.99 < weight_sum < 1.01):  # Allow small floating point error
            raise ValueError(
                f"consensus_weight_ratio + consensus_weight_score must sum to 1.0, "
                f"got {weight_sum}"
            )

    def hold_vote(self, proposal: Dict[str, float]) -> VoteResult:
        """Run a vote and compute a consensus score from member evaluations.

        Args:
            proposal: Dict with keys 'human_benefit', 'safety', 'feasibility'.
                Each value should be a float between 0.0 and 1.0.

        Returns:
            VoteResult containing:
                - evaluations: List of individual agent evaluations
                - approval_ratio: Fraction of agents voting "approve"
                - average_score: Mean weighted score across all agents
                - consensus_score: Final consensus metric (0.0-1.0)
                - consensus_reached: True if consensus_score >= threshold
                - explanation: Human-readable summary of the result

        Raises:
            ValueError: If proposal is missing required keys or has invalid values.
        """
        self._validate_proposal(proposal)

        evaluations = [agent.evaluate_proposal(proposal) for agent in self.agents]
        approvals = [item for item in evaluations if item["vote"] == "approve"]

        approval_ratio = len(approvals) / len(self.agents)
        average_score = (
            sum(float(item["score"]) for item in evaluations) / len(evaluations)
        )

        consensus_score = round(
            (approval_ratio * self.consensus_weight_ratio)
            + (average_score * self.consensus_weight_score),
            4,
        )
        consensus_reached = consensus_score >= self.consensus_threshold

        explanation = self._explain_consensus(
            consensus_reached, consensus_score, approval_ratio, average_score
        )

        logger.info(
            f"Council vote completed: consensus_reached={consensus_reached}, "
            f"consensus_score={consensus_score}, approval_ratio={approval_ratio}"
        )

        return VoteResult(
            evaluations=evaluations,
            approval_ratio=round(approval_ratio, 4),
            average_score=round(average_score, 4),
            consensus_score=consensus_score,
            consensus_reached=consensus_reached,
            explanation=explanation,
        )

    def _validate_proposal(self, proposal: Dict[str, float]) -> None:
        """Validate proposal structure and values.

        Args:
            proposal: Dict to validate.

        Raises:
            ValueError: If proposal is invalid.
        """
        missing_keys = REQUIRED_PROPOSAL_KEYS - set(proposal.keys())
        if missing_keys:
            raise ValueError(
                f"Proposal missing required keys: {missing_keys}. "
                f"Required: {REQUIRED_PROPOSAL_KEYS}"
            )

        for key, value in proposal.items():
            if key in REQUIRED_PROPOSAL_KEYS:
                try:
                    float_val = float(value)
                    if not 0.0 <= float_val <= 1.0:
                        raise ValueError(
                            f"Proposal key '{key}' must be between 0.0 and 1.0, "
                            f"got {float_val}"
                        )
                except (TypeError, ValueError) as e:
                    raise ValueError(
                        f"Proposal key '{key}' must be a valid number between 0.0 and 1.0"
                    ) from e

    def _explain_consensus(
        self,
        consensus_reached: bool,
        consensus_score: float,
        approval_ratio: float,
        average_score: float,
    ) -> str:
        """Generate human-readable explanation of consensus result.

        Args:
            consensus_reached: Whether consensus was achieved.
            consensus_score: Final consensus score.
            approval_ratio: Fraction of approving agents.
            average_score: Mean evaluation score.

        Returns:
            Formatted explanation string.
        """
        status = "CONSENSUS REACHED" if consensus_reached else "CONSENSUS FAILED"
        approval_pct = round(approval_ratio * 100, 1)
        threshold_pct = round(self.consensus_threshold * 100, 1)

        return (
            f"{status}: Score {consensus_score:.4f} "
            f"({approval_pct}% approval, {average_score:.4f} avg score) "
            f"vs threshold {threshold_pct}%"
        )


def default_council() -> Council:
    """Create a default council for demo use.

    Returns:
        A Council instance with three representative agents.
    """
    return Council(
        agents=[
            BaseAgent(name="Ada", role="Safety Steward"),
            BaseAgent(name="Lin", role="Public Benefit Analyst"),
            BaseAgent(name="Noor", role="Implementation Reviewer"),
        ]
    )
