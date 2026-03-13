"""Streamlit dashboard for AnnabanAI governance transparency."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from dashboard.metrics import count_human_vetoes, summarize_votes

st.set_page_config(page_title="AnnabanAI Dashboard", page_icon="🧭", layout="wide")

st.title("AnnabanAI Governance Dashboard (Prototype)")
st.caption("Human-sovereign governance, transparent logs, and conceptual value-return routing.")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
MOCK_PATH = BASE_DIR / "data_mock.json"


def load_json(path: Path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_dashboard_payload():
    # Try environment logs first; fallback to static mock data.
    actions = load_json(DATA_DIR / "actions_log.json")
    votes = load_json(DATA_DIR / "votes_log.json")
    vetoes = load_json(DATA_DIR / "human_veto_events.json")

    if actions or votes or vetoes:
        return {
            "governance_status": {
                "mode": "prototype-live-logs",
                "human_sovereignty": "enabled",
                "transparency_logging": "active",
            },
            "council_vote_results": [
                {
                    "proposal_id": item.get("proposal_id"),
                    "consensus_score": item.get("vote_result", {}).get("consensus_score", 0.0),
                    "consensus_reached": item.get("vote_result", {}).get("consensus_reached", False),
                }
                for item in votes
            ],
            "human_veto_events": vetoes,
            "revision_log": [
                "Live mode: using environment JSON logs.",
                "Fallback mode: dashboard/data_mock.json",
            ],
            "contributors": [
                "Human Author - Project Steward",
                "Human Author - Community Reviewer",
            ],
        }

    return load_json(MOCK_PATH)


payload = load_dashboard_payload()

status = payload.get("governance_status", {})
with st.container(border=True):
    st.subheader("Governance Status")
    col1, col2, col3 = st.columns(3)
    col1.metric("Mode", status.get("mode", "unknown"))
    col2.metric("Human Sovereignty", status.get("human_sovereignty", "unknown"))
    col3.metric("Transparency Logging", status.get("transparency_logging", "unknown"))

votes = payload.get("council_vote_results", [])
metrics = summarize_votes([
    {"vote_result": {"consensus_score": item.get("consensus_score", 0.0)}} for item in votes
])

with st.container(border=True):
    st.subheader("Council Vote Results")
    st.metric("Total Votes", metrics["count"])
    st.metric("Average Consensus Score", metrics["avg_consensus"])
    st.dataframe(votes, use_container_width=True)

veto_events = payload.get("human_veto_events", [])
with st.container(border=True):
    st.subheader("Human Veto Events")
    st.metric("Triggered Vetoes", count_human_vetoes(veto_events))
    st.dataframe(veto_events, use_container_width=True)

with st.container(border=True):
    st.subheader("Revision Log")
    for item in payload.get("revision_log", []):
        st.write(f"- {item}")

with st.container(border=True):
    st.subheader("Contributor List")
    for person in payload.get("contributors", []):
        st.write(f"- {person}")

st.info(
    "All outputs in this prototype are simulations intended for human-led governance research."
)
