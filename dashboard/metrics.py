"""Utility helpers for Streamlit dashboard metrics."""

from __future__ import annotations

from typing import Dict, List


def summarize_votes(votes: List[Dict[str, object]]) -> Dict[str, float]:
    if not votes:
        return {"count": 0, "avg_consensus": 0.0}

    consensus_scores = [
        float(item.get("vote_result", {}).get("consensus_score", 0.0)) for item in votes
    ]
    return {
        "count": len(votes),
        "avg_consensus": round(sum(consensus_scores) / len(consensus_scores), 4),
    }


def count_human_vetoes(veto_events: List[Dict[str, object]]) -> int:
    return sum(1 for event in veto_events if event.get("veto_triggered", False))
