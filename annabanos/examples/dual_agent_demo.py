"""Dual-agent demo: planner + oversight with governance-first handling."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from annaban.governance import AnnabanGovernance
from annaban.grok_client import GrokClient
from annaban.ledger import GovernanceLedger
from annaban.tools import call_tool


PLANNER_SYSTEM_PROMPT = (
    "You are the Planner Agent. Produce efficient, step-by-step plans focused on optimization."
)

OVERSIGHT_SYSTEM_PROMPT = (
    "You are the Oversight Agent. Review plans for safety, governance, and policy compliance."
)


def run_demo() -> None:
    load_dotenv()
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing XAI_API_KEY. Create a .env file from .env.example.")

    origin = call_tool("verify_origin")
    print(f"Tool output (verify_origin): {origin}\n")

    client = GrokClient(api_key=api_key, model="grok-4.20")
    ledger = GovernanceLedger(ledger_path="logs/governance_ledger.jsonl")
    governance = AnnabanGovernance(grok_client=client, ledger=ledger)

    task = "Design a migration plan for moving a legacy web service to a containerized platform."

    planner_output = governance.process(
        prompt=task,
        system_prompt=PLANNER_SYSTEM_PROMPT,
    )

    oversight_prompt = (
        "Review this planner output for governance and safety concerns. "
        "Recommend controls and approval gates where needed.\n\n"
        f"Planner output:\n{planner_output}"
    )
    oversight_output = governance.process(
        prompt=oversight_prompt,
        system_prompt=OVERSIGHT_SYSTEM_PROMPT,
    )

    print("=== Planner Agent Output ===")
    print(planner_output)
    print("\n=== Oversight Agent Output ===")
    print(oversight_output)


if __name__ == "__main__":
    run_demo()
