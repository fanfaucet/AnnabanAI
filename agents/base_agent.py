"""Base agent model for the AnnabanAI governance prototype.

This module is intentionally lightweight and beginner-friendly.
It avoids external AI model dependencies and uses transparent scoring rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class BaseAgent:
    """A simple governance agent that evaluates proposals with rubric weights.

    Attributes:
        name: Human-readable agent name.
        role: Responsibility area in the council.
        rubric_weights: Importance weights for proposal dimensions.
    """

    name: str
    role: str
    rubric_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "human_benefit": 0.45,
            "safety": 0.3,
            "feasibility": 0.25,
        }
    )

    def evaluate_proposal(self, proposal: Dict[str, float]) -> Dict[str, object]:
        """Return a transparent score and vote for a proposal.

        Args:
            proposal: Dict containing numeric values from 0.0 to 1.0 for each rubric key.

        Returns:
            Structured dict with score, vote, and reasoning strings.
        """

        weighted_score = 0.0
        reasoning: List[str] = []

        for key, weight in self.rubric_weights.items():
            value = float(proposal.get(key, 0.0))
            weighted_score += value * weight
            reasoning.append(
                f"{key}={value:.2f} × weight {weight:.2f} contributes {value * weight:.2f}"
            )

        vote = "approve" if weighted_score >= 0.65 else "reject"

        return {
            "agent": self.name,
            "role": self.role,
            "score": round(weighted_score, 4),
            "vote": vote,
            "reasoning": reasoning,
        }
